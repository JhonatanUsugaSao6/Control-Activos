from django.db import connection, transaction
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib import messages
from django.http import HttpResponseServerError
from django.contrib.auth.decorators import login_required
from django.db import connections
from ControlActivos.models import ValidacionTri, ValidacionManual
import logging

logger = logging.getLogger(__name__)


def inicio(request):
    return render(request, 'base.html')



def obtener_datos_validacion(i, request):
    """Obtiene los datos de cada campo para la validación."""
    return {
        "motivo_fecha": request.POST.get(f"motivo_fecha_{i}"),
        "motivo_descripcion": request.POST.get(f"motivo_descripcion_{i}"),
        "motivo_cantidad": request.POST.get(f"motivo_cantidad_{i}"),
        "motivo_ubicacion": request.POST.get(f"motivo_ubicacion_{i}"),
        "motivo_sello": request.POST.get(f"motivo_sello_{i}"),
        "motivo_firmaalmacen": request.POST.get(f"motivo_firmaalmacen_{i}"),
        "motivo_firmaproveedor": request.POST.get(f"motivo_firmaproveedor_{i}"),
        "motivo_marcacion": request.POST.get(f"motivo_marcacion_{i}"),
    }




@login_required
def validarTri(request):
    if request.method == "POST":
        
        tipo = request.POST.get("tipo_ingreso", "") 

        if tipo == "manual":
            numero_manual = request.POST.get("numero_manual", "").strip()
            foto_manual = request.FILES.get("foto_manual")

            if numero_manual and foto_manual:
                ValidacionManual.objects.create(
                    numero_manual=numero_manual,
                    ruta_imagen=foto_manual,  # Django se encarga del guardado
                    vigilante=request.user
                )
                messages.success(request, "Salida manual guardada exitosamente.")
            else:
                messages.error(request, "Debes ingresar el número y seleccionar una imagen.")
            
            return redirect('validarTri')
        
        
        try:
            total_items_raw = request.POST.get("total_items", "0")
            total_items = int(total_items_raw)
            logger.debug(f"Total de ítems a validar: {total_items}")

            validaciones = []

            consecutivo = request.POST.get("consecutivo", "").strip()
            logger.debug(f"Consecutivo recibido: {consecutivo}")
            
            
            
            
            
            for i in range(total_items):
                
                referencia = request.POST.get(f"referencia_{i}", "").strip()
                logger.debug(f"Referencia recibida: {referencia}")

                datos_val = obtener_datos_validacion(i, request)

               

                with connections['sql'].cursor() as cursor:
                    cursor.execute("""
                        SELECT
                            bod.f150_descripcion,
                            inv.f470_cant_1,
                            inv.f470_id_unidad_medida,
                            ubic.f155_descripcion,
                            v.v121_descripcion,
                            v.v121_id_ext1_detalle
                        FROM t470_cm_movto_invent AS inv
                        INNER JOIN t350_co_docto_contable AS cont ON inv.f470_rowid_docto = cont.f350_rowid
                        LEFT JOIN t150_mc_bodegas AS bod ON inv.f470_rowid_bodega = bod.f150_rowid
                        LEFT JOIN (
                            SELECT f155_id, MIN(f155_descripcion) AS f155_descripcion
                            FROM t155_mc_ubicacion_auxiliares
                            GROUP BY f155_id
                        ) AS ubic ON inv.f470_id_ubicacion_aux = ubic.f155_id
                        LEFT JOIN v121 AS v ON inv.f470_rowid_item_ext = v.v121_rowid_item_ext
                        WHERE cont.f350_consec_docto = %s
                        AND v.v121_referencia = %s
                        AND inv.f470_id_cia = 4
                        AND cont.f350_id_tipo_docto = 'TRI'
                        AND inv.f470_ind_naturaleza = 1
                        AND bod.f150_descripcion IN (
                            'BODEGA CARRO TALLER INTERNO',
                            'BODEGA GARANTIAS',
                            'BODEGA PNC MANTENIMIENTO',
                            'BODEGA PRODUCTO NO CONFORME',
                            'BODEGA PROVEEDORES',
                            'BODEGA REPARACIONES',
                            'BODEGA TRANSITO MANTENIMIENTO'
                        )
                    """, [consecutivo, referencia])

                    row = cursor.fetchone()

                if row:
                    bodega, cantidad, unidad_medida, ubicacion, descripcion, extension = row

                    logger.debug(f"Datos obtenidos de la DB para {referencia}")
                    logger.debug(f"  Bodega: {bodega}, Cantidad: {cantidad}, Unidad: {unidad_medida}, Ubicación: {ubicacion}, Desc: {descripcion}, Ext: {extension}")
                    
                    valores = [str(datos_val.get(k, '')) for k in datos_val]
                    cadena_validacion = ",".join(valores)
                    
                    validacion_obj = ValidacionTri(
                        consecutivo=consecutivo,
                        referencia=referencia,
                        descripcion=descripcion or "",
                        bodega=bodega or "",
                        extension=extension or "",
                        unidad_medida=unidad_medida or "",
                        cantidad=cantidad or 0,
                        ubicacion=ubicacion or "",  
                        validacion=cadena_validacion,
                        vigilante=request.user
                    )
                    
                    validaciones.append(validacion_obj)
                    
                else:
                    logger.debug(f"⚠ No se encontró información en la BD para la referencia '{referencia}' con consecutivo '{consecutivo}'")
            
            

            if validaciones:
                logger.debug(f"Total de objetos a guardar: {len(validaciones)}")
                
                with transaction.atomic():
                    ValidacionTri.objects.bulk_create(validaciones, batch_size=100)
                messages.success(request, "Validaciones guardadas exitosamente.")
            else:
                logger.debug("⚠ No hay validaciones para guardar.")
                messages.warning(request, "No se encontraron datos válidos para guardar.")

        except ValueError as e:
            logger.debug(f"❌ Error de conversión de número: {e}")
            return HttpResponseServerError(f"<h1>Error: total_items no es un número válido.</h1><p>{e}</p>")
        except Exception as e:
            logger.debug(f"❌ Error inesperado: {e}")
            messages.error(request, f"Error al guardar validaciones: {e}")
            return redirect('validarTri')



    # Método GET (búsqueda)
    consecutivo = request.GET.get('consecutivo', '').strip()
    resultado = []

    if consecutivo:
        try:
            with connections['sql'].cursor() as cursor:
                cursor.execute("""
                    SELECT
                        bod.f150_descripcion AS bodega_descripcion,
                        inv.f470_cant_1,
                        inv.f470_id_unidad_medida,                        
                        ubic.f155_descripcion AS ubicacion_descripcion,
                        cont.f350_consec_docto,
                        cont.f350_fecha, 
                        cont.f350_usuario_aprobacion,
                        cont.f350_id_tipo_docto,
                        v.v121_descripcion,
                        v.v121_referencia,
                        v.v121_id_ext1_detalle,
                        inv.f470_costo_est_tot,
                        inv.f470_id_fecha                        
                    FROM t470_cm_movto_invent AS inv
                    INNER JOIN t350_co_docto_contable AS cont ON inv.f470_rowid_docto = cont.f350_rowid
                    LEFT JOIN t150_mc_bodegas AS bod ON inv.f470_rowid_bodega = bod.f150_rowid
                    LEFT JOIN (
                        SELECT f155_id, MIN(f155_descripcion) AS f155_descripcion
                        FROM t155_mc_ubicacion_auxiliares
                        GROUP BY f155_id
                    ) AS ubic ON inv.f470_id_ubicacion_aux = ubic.f155_id
                    LEFT JOIN v121 AS v ON inv.f470_rowid_item_ext = v.v121_rowid_item_ext
                    WHERE cont.f350_consec_docto = %s
                    AND inv.f470_id_cia = 4 
                    AND cont.f350_id_tipo_docto = 'TRI'
                    AND inv.f470_ind_naturaleza = 1
                    AND bod.f150_descripcion IN (
                        'BODEGA CARRO TALLER INTERNO',
                        'BODEGA GARANTIAS',
                        'BODEGA PNC MANTENIMIENTO',
                        'BODEGA PRODUCTO NO CONFORME',
                        'BODEGA PROVEEDORES',
                        'BODEGA REPARACIONES',
                        'BODEGA TRANSITO MANTENIMIENTO'
                    )
                """, [consecutivo])
                
                rows = cursor.fetchall()
                
                resultado = [{
                    'Bodega': str(row[0]),
                    'Cantidad': int(row[1]) if row[1] is not None else '',
                    'UnidadMedida': row[2].strip(),                       
                    'Ubicacion': row[3],                      
                    'Fecha350': row[5].strftime("%Y-%m-%d") if row[5] else '',
                    'Usuario': row[6],
                    'TipoDoct': row[7],
                    'Descripcion': row[8],
                    'Referencia': row[9],
                    'Detalle': row[10],
                    'CostoTotal': float(row[11]),
                    'Fecha': row[12],
                } for row in rows]

        except Exception as e:
            logger.debug(f"Error al obtener datos: {e}")

    return render(request, 'Tri/formulario.html', {'resultado': resultado, 'consecutivo': consecutivo})




@login_required
def listadoValidaciones(request):   
    tris = ValidacionTri.objects.all()
    for tri in tris:
        validaciones = [v.strip() for v in tri.validacion.split(',') if v.strip() != "None" and v.strip()]
        tri.validacion_limpia = ', '.join(validaciones) if validaciones else "Sin novedad"

    return render(request, "Tri/listadoTri.html", {'tris': tris})



@login_required
def listadoValidacionesManuales(request):   
    tris = ValidacionManual.objects.all()
    return render(request, "Tri/listadoManuales.html", {'tris': tris})



def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            return redirect('validarTri')  
        else:
            messages.error(request, 'Credenciales inválidas')
    return render(request, 'Login/login.html')  




def logout_view(request):
    logout(request)
    return redirect('login')