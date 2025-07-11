from django.db import connection, transaction
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib import messages
from django.http import HttpResponseServerError
from django.contrib.auth.decorators import login_required
from django.db import connections
from ControlActivos.models import ValidacionTri, ValidacionManual, ValidacionLlantas, EvidenciaLlantas, EvidenciaTris
import logging
from django.db.models import Max
from django.http import JsonResponse
from django.utils.timezone import localtime
from django.core.paginator import Paginator




logger = logging.getLogger(__name__)


def inicio(request):
    return render(request, 'base.html')



def obtener_datos_validacion(i, request):
    """Obtiene los datos de cada campo para la validación."""
    return {
        "Fecha": request.POST.get("fecha"),
        "Descripción": request.POST.get(f"motivo_descripcion_{i}"),
        "Cantidad": request.POST.get(f"motivo_cantidad_{i}"),
        "Proveedor": request.POST.get("cumple_proveedor"),
        "Sello": request.POST.get("sello"),
        "Firma Almacén": request.POST.get("firma_almacen"),
        "Firma Proveedor": request.POST.get("firma_proveedor"),
        "Marcación": request.POST.get(f"motivo_marcacion_{i}"),
    }


def obtener_datos_validacion_llantas(i, request):
    """Obtiene los datos de cada campo para la validación."""
    return {
        "Fecha": request.POST.get("fecha"),
        "Descripción": request.POST.get(f"motivo_descripcion_{i}"),
        "Proveedor": request.POST.get(f"cumple_proveedor"),
        "Sello": request.POST.get("sello"),
        "Firma Almacén": request.POST.get("firma_almacen"),
        "Firma Proveedor": request.POST.get("firma_proveedor"),
        "Marcación": request.POST.get(f"motivo_marcacion_{i}"),
        "Serial": request.POST.get(f"motivo_serial_{i}"),
        "Quemado": request.POST.get(f"motivo_quemado_{i}"),
        "VIN": request.POST.get(f"motivo_vin_{i}"),
        "Documento Anexo": request.POST.get(f"documento_anexo"),
    }






@login_required
def validarTri(request):
    if request.method == "POST":
        
        tipo = request.POST.get("tipo_ingreso", "") 
        print(f"Tipo {tipo}")
        tipo_salida = request.POST.get("tipo_salida", "")
        print(f"Tipo de salida {tipo_salida}")

        if tipo == "manual":
            numero_manual = request.POST.get("numero_manual", "").strip()
            concepto_salida = request.POST.get("concepto_salida")            
            motivo_retiro = request.POST.get("motivo_retiro")               
            foto_manual = request.FILES.get("foto_manual")
            firma_almacen = request.POST.get("firma_almacen")
            firma_autorizacion = request.POST.get("firma_autorizacion")

            firma_proveedor = request.POST.get("firma_proveedor")
            sello = request.POST.get("sello")
            tachones_enmendaduras = request.POST.get("tachones_enmendaduras")
            
            ahora = localtime()

            if numero_manual and foto_manual and firma_almacen and firma_proveedor and sello and concepto_salida:
                ValidacionManual.objects.create(
                    fecha=ahora.date(),        
                    hora=ahora.time(),        
                    numero_manual=numero_manual,
                    concepto_salida=concepto_salida,
                    ruta_imagen=foto_manual,
                    motivo_retiro=motivo_retiro,
                    validacion_firma_almacen=firma_almacen,
                    validacion_firma_autorizacion=firma_autorizacion,
                    validacion_firma_proveedor=firma_proveedor,
                    validacion_sello=sello,
                    validacion_tachones_enmendaduras=tachones_enmendaduras,
                    
                    vigilante=request.user
                )
                messages.success(request, "Salida manual guardada exitosamente.")
            else:
                messages.error(request, "Todos los campos son obligatorios")

            return redirect('validarTri')
        
        
        
        
        #Salisa por consecutivo
        elif tipo_salida == "consecutivo":
              
            try:
                total_items_raw = request.POST.get("total_items", "0")
                total_items = int(total_items_raw)
                logger.debug(f"Total de ítems a validar: {total_items}")

                foto_tri = request.FILES.get("foto_tri")
                
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
                        
                        ahora = localtime()
                        
                        validacion_obj = ValidacionTri(
                            fecha=ahora.date(),               
                            hora=ahora.time(), 
                            consecutivo=consecutivo,
                            referencia=referencia,
                            descripcion=descripcion or "",
                            bodega=bodega or "",
                            extension=extension or "",
                            unidad_medida=unidad_medida or "",
                            cantidad=cantidad or 0,
                            ubicacion=ubicacion or "",
                            validacion_descripcion=datos_val.get("Descripción"),
                            validacion_cantidad=datos_val.get("Cantidad"),
                            validacion_proveedor=datos_val.get("Proveedor"),
                            validacion_marcacion=datos_val.get("Marcación"),
                            validacion_fecha_tri=datos_val.get("Fecha"),
                            validacion_sello=datos_val.get("Sello"),
                            validacion_firma_almacen=datos_val.get("Firma Almacén"),
                            validacion_firma_proveedor=datos_val.get("Firma Proveedor"),
                            evidencia_tri=foto_tri,

                            vigilante=request.user
                        )
                        
                        validaciones.append(validacion_obj)
                
                
                if validaciones:
                    with transaction.atomic():
                        ValidacionTri.objects.bulk_create(validaciones, batch_size=100)

                        nuevas_validaciones = list(
                            ValidacionTri.objects.filter(
                                consecutivo=consecutivo,
                                vigilante=request.user
                            ).order_by('-id')[:total_items]
                        )
                        nuevas_validaciones.reverse()

                        evidencias = []
                        for key, archivo in request.FILES.items():
                            if not key.startswith("foto_"):
                                continue

                            partes = key.split("_")
                            if len(partes) < 3:
                                continue

                            tipo = partes[1]  # ejemplo: fecha, vin, etc.
                            categoria = partes[2]

                            try:
                                if categoria == "general":
                                    # Evidencias generales: puedes usar la primera validación como referencia
                                    index = 0
                                else:
                                    index = int(categoria)
                            except ValueError:
                                continue

                            if 0 <= index < len(nuevas_validaciones):
                                evidencias.append(EvidenciaTris(
                                    ruta=archivo,
                                    fecha=localtime().date(),
                                    tipo=tipo.capitalize(),
                                    tri=nuevas_validaciones[index]
                                ))

                        if evidencias:
                            EvidenciaTris.objects.bulk_create(evidencias)                        
                        
                    messages.success(request, "Validaciones guardadas exitosamente.")
                else:
                    messages.warning(request, "No se encontraron datos válidos para guardar.")

                return redirect('validarTri')    
                
            except ValueError as e:
                logger.debug(f"❌ Error de conversión de número: {e}")
                return HttpResponseServerError(f"<h1>Error: total_items no es un número válido.</h1><p>{e}</p>")
            except Exception as e:
                logger.debug(f"❌ Error inesperado: {e}")
                messages.error(request, f"Error al guardar validaciones: {e}")
                return redirect('validarTri')
        
        
        
        elif tipo_salida == "consecutivo llantas":
            try:
                total_items_raw = request.POST.get("total_items", "0")
                if not total_items_raw.isdigit():
                    raise ValueError(f"Valor no numérico recibido: {total_items_raw}")
                total_items = int(total_items_raw)

                validacionesLlantas = []
                consecutivo_llantas = request.POST.get("consecutivo_llantas", "").strip()

                for i in range(total_items):
                    quemado = request.POST.get(f"quemado{i}", "").strip()
                    datos_val = obtener_datos_validacion_llantas(i, request)

                    with connections['sql'].cursor() as cursor:
                        cursor.execute("""
                            SELECT
                                bod.f150_descripcion,
                                ubic.f155_descripcion,
                                v.v121_descripcion,
                                v.v121_id_ext1_detalle,
                                srl.f417_campo_1,
                                srl.f417_id,
                                v.v121_referencia
                            FROM t470_cm_movto_invent AS inv
                            INNER JOIN t350_co_docto_contable AS cont ON inv.f470_rowid_docto = cont.f350_rowid
                            LEFT JOIN t150_mc_bodegas AS bod ON inv.f470_rowid_bodega = bod.f150_rowid
                            LEFT JOIN (
                                SELECT f155_id, MIN(f155_descripcion) AS f155_descripcion
                                FROM t155_mc_ubicacion_auxiliares
                                GROUP BY f155_id
                            ) AS ubic ON inv.f470_id_ubicacion_aux = ubic.f155_id
                            LEFT JOIN v121 AS v ON inv.f470_rowid_item_ext = v.v121_rowid_item_ext
                            INNER JOIN t479_cm_movto_seriales AS ms ON ms.f479_rowid_movto_inv = inv.f470_rowid
                            INNER JOIN t417_cm_seriales AS srl ON ms.f479_rowid_serial = srl.f417_rowid
                            WHERE cont.f350_consec_docto = %s
                            AND srl.f417_campo_2 = %s
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
                            AND srl.f417_id_cfg_serial = 1
                        """, [consecutivo_llantas, quemado])
                        row = cursor.fetchone()

                    if row:
                        bodega, ubicacion, descripcion, extension, vin, serial, referencia = row
                        ahora = localtime()
                        validacion_obj_llantas = ValidacionLlantas(
                            fecha=ahora.date(),
                            hora=ahora.time(),
                            consecutivo=consecutivo_llantas,
                            referencia=referencia,
                            descripcion=descripcion or "",
                            bodega=bodega or "",
                            extension=extension or "",
                            ubicacion=ubicacion or "",
                            serial=serial,
                            quemado=quemado,
                            vin=vin,
                            validacion_descripcion=datos_val.get("Descripción"),
                            validacion_serial=datos_val.get("Serial"),
                            validacion_quemado=datos_val.get("Quemado"),
                            validacion_vin=datos_val.get("VIN"),
                            validacion_proveedor=datos_val.get("Proveedor"),
                            validacion_fecha_llantas=datos_val.get("Fecha"),
                            validacion_documento_anexo=datos_val.get("Documento Anexo"),
                            validacion_sello=datos_val.get("Sello"),
                            validacion_firma_almacen=datos_val.get("Firma Almacén"),
                            validacion_firma_proveedor=datos_val.get("Firma Proveedor"),
                            vigilante=request.user
                        )
                        validacionesLlantas.append(validacion_obj_llantas)

                if validacionesLlantas:
                    with transaction.atomic():
                        ValidacionLlantas.objects.bulk_create(validacionesLlantas, batch_size=100)

                        nuevas_validaciones = list(
                            ValidacionLlantas.objects.filter(
                                consecutivo=consecutivo_llantas,
                                vigilante=request.user
                            ).order_by('-id')[:total_items]
                        )
                        nuevas_validaciones.reverse()

                        evidencias = []
                        for key, archivo in request.FILES.items():
                            if not key.startswith("foto_"):
                                continue

                            partes = key.split("_")
                            if len(partes) < 3:
                                continue

                            tipo = partes[1]  # ejemplo: fecha, vin, etc.
                            categoria = partes[2]

                            try:
                                if categoria == "general":
                                    # Evidencias generales: puedes usar la primera validación como referencia
                                    index = 0
                                else:
                                    index = int(categoria)
                            except ValueError:
                                continue

                            if 0 <= index < len(nuevas_validaciones):
                                evidencias.append(EvidenciaLlantas(
                                    ruta=archivo,
                                    fecha=localtime().date(),
                                    tipo=tipo.capitalize(),
                                    llanta=nuevas_validaciones[index]
                                ))

                        if evidencias:
                            EvidenciaLlantas.objects.bulk_create(evidencias)

                    messages.success(request, "Validaciones llantas guardadas exitosamente.")
                else:
                    messages.warning(request, "No se encontraron datos válidos para guardar.")

                return redirect('validarTri')

            except ValueError as e:
                return HttpResponseServerError(f"<h1>Error: total_items no es un número válido.</h1><p>{e}</p>")
            except Exception as e:
                messages.error(request, f"Error al guardar validaciones llantas: {e}")
                return redirect('validarTri')
        
        

    # Método GET (búsqueda)
    elif request.method == "GET":
        consecutivo = request.GET.get('consecutivo', '').strip()
        consecutivo_llantas = request.GET.get('consecutivo_llantas', '').strip()
        resultado = []

        if consecutivo:
            print(f"Consecutivo recibido: {consecutivo}")

            # Verificamos si existen registros para ese consecutivo
            existe = ValidacionTri.objects.filter(consecutivo=consecutivo).exists()

            if existe:
                # Subconsulta para obtener el último registro por referencia
                subconsulta = (
                    ValidacionTri.objects
                    .filter(consecutivo=consecutivo)
                    .values('referencia')
                    .annotate(ultimo_id=Max('id'))
                    .values_list('ultimo_id', flat=True)
                )

                ultimos_registros = ValidacionTri.objects.filter(id__in=subconsulta)

                print(f"Últimos registros válidos para el consecutivo {consecutivo}:")
                for r in ultimos_registros:
                    print(f"{r.referencia} => {r.validacion_descripcion}, {r.validacion_proveedor}, etc.")

                todas_correctas = True
                for val in ultimos_registros:
                    campos_validacion = [
                        val.validacion_descripcion,
                        val.validacion_proveedor,
                        val.validacion_marcacion,
                        val.validacion_fecha_tri,
                        val.validacion_sello,
                        val.validacion_firma_almacen,
                        val.validacion_firma_proveedor
                    ]

                    for campo in campos_validacion:
                        if str(campo).strip().lower() not in ['correcto', 'correcta']:
                            todas_correctas = False
                            break

                if todas_correctas:
                    messages.warning(request, f"El número de consecutivo '{consecutivo}' ya fue registrado completamente.")
                    return render(request, 'Tri/formulario.html', {'resultado': [], 'consecutivo': consecutivo})

            # Si no existe en ValidacionTri o no está completamente registrado, entonces consultamos el sistema externo
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
                        'Fecha350': row[5].strftime("%d/%m/%Y") if row[5] else '',
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

        
        if consecutivo_llantas:
            print(f"Consecutivo llantas recibido: {consecutivo_llantas}")

            # Verificamos si existen registros para ese consecutivo
            existe = ValidacionLlantas.objects.filter(consecutivo=consecutivo_llantas).exists()
            print(f"La consulta existe muestra {existe}")

            if existe:
                # Subconsulta para obtener el último registro por referencia
                subconsulta = (
                    ValidacionLlantas.objects
                    .filter(consecutivo=consecutivo_llantas)
                    .values('referencia')
                    .annotate(ultimo_id=Max('id'))
                    .values_list('ultimo_id', flat=True)
                )

                ultimos_registros = ValidacionLlantas.objects.filter(id__in=subconsulta)
                print(f"Últimos registros del consecutivo {ultimos_registros}")

                print(f"Últimos registros válidos para el consecutivo {consecutivo_llantas}:")
                for r in ultimos_registros:
                    print(f"{r.referencia} => {r.validacion_descripcion}, {r.validacion_serial}, {r.validacion_quemado}, etc.")

                # Mostrar mensaje siempre que el consecutivo exista
                messages.warning(request, f"El número de consecutivo de llantas '{consecutivo_llantas}' ya fue registrado previamente.")
                return render(request, 'Tri/formulario.html', {'resultado': [], 'consecutivo': consecutivo_llantas})


            
            # Si no existe en ValidacionLlantas o no está completamente registrado, entonces consultamos el sistema externo
            try:
                print("Entrando al tri cuando no existe registro")
                with connections['sql'].cursor() as cursor:
                    print("Entrado al with para la consulta")
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
                            inv.f470_id_fecha,
                            
                            srl.f417_campo_1,
                            srl.f417_id,
                            srl.f417_campo_2,
                            inv.f470_rowid_item_ext,                       
                            inv.f470_rowid_docto,
                            inv.f470_rowid_bodega,
                            inv.f470_id_ubicacion_aux
                            
                            
                        FROM t470_cm_movto_invent AS inv
                        INNER JOIN t350_co_docto_contable AS cont ON inv.f470_rowid_docto = cont.f350_rowid
                        LEFT JOIN t150_mc_bodegas AS bod ON inv.f470_rowid_bodega = bod.f150_rowid
                        LEFT JOIN (
                            SELECT f155_id, MIN(f155_descripcion) AS f155_descripcion
                            FROM t155_mc_ubicacion_auxiliares
                            GROUP BY f155_id
                        ) AS ubic ON inv.f470_id_ubicacion_aux = ubic.f155_id
                        LEFT JOIN v121 AS v ON inv.f470_rowid_item_ext = v.v121_rowid_item_ext
                        INNER JOIN t479_cm_movto_seriales AS ms ON ms.f479_rowid_movto_inv = inv.f470_rowid
                        INNER JOIN t417_cm_seriales AS srl ON ms.f479_rowid_serial = srl.f417_rowid
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
                        AND srl.f417_id_cfg_serial = 1
                    """, [consecutivo_llantas])
                    
                    rows = cursor.fetchall()
                    
                    
                    resultado = [{
                        'Bodega': str(row[0]),                       
                        'Ubicacion': row[3],                      
                        'Fecha350': row[5].strftime("%d/%m/%Y") if row[5] else '',
                        'Usuario': row[6],
                        'TipoDoct': row[7],
                        'Descripcion': row[8],
                        'Referencia': row[9],
                        'Detalle': row[10],
                        'CostoTotal': float(row[11]),
                        'Fecha': row[12],    
                        'Serial': row[14],                        
                        'Vin': row[13],     
                        'Quemado': row[15],                                                          
                        'ItemExt': row[16],                                              
                        'DoctoInvent': row[17],                     
                
                    } for row in rows]

            except Exception as e:
                logger.debug(f"Error al obtener datos: {e}")
            
        
        
        return render(request, 'Tri/formulario.html', {'resultado': resultado, 'consecutivo': consecutivo, 'consecutivo_llantas': consecutivo_llantas,})




@login_required
def listadoValidaciones(request):   
    filtro = request.GET.get("filtro", "")
    tris_qs = ValidacionTri.objects.all().order_by("-id")

    if filtro:
        tris_qs = tris_qs.filter(consecutivo__icontains=filtro)

    paginator = Paginator(tris_qs, 20)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    for tri in page_obj:
        validaciones = []
        campos_validacion = {
            "Descripción": tri.validacion_descripcion,
            "Cantidad": tri.validacion_cantidad,
            "Proveedor": tri.validacion_proveedor,
            "Marcacion": tri.validacion_marcacion,
            "Fecha": tri.validacion_fecha_tri,
            "Sello": tri.validacion_sello,
            "Firma almacén": tri.validacion_firma_almacen,
            "Firma proveedor": tri.validacion_firma_proveedor,
        }

        for campo, valor in campos_validacion.items():
            valor_str = str(valor).strip().lower()
            if valor_str not in ["correcto", "correcta"]:
                validaciones.append(f"{campo}: {valor}")

        tri.validacion_limpia = ', '.join(validaciones) if validaciones else "Sin novedad"

        # Obtener evidencias relacionadas y agregar fecha formateada
        evidencias = EvidenciaTris.objects.filter(tri=tri)
        for evidencia in evidencias:
            evidencia.fecha_formateada = evidencia.fecha.strftime("%d/%m/%Y")
        tri.evidencias = evidencias

    return render(request, "Tri/listadoTri.html", {'tris': page_obj})



@login_required
def listadoLlantas(request):
    llantas_qs = ValidacionLlantas.objects.all().order_by("-id")

    paginator = Paginator(llantas_qs, 20)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    for llanta in page_obj:
        validaciones = []
        campos_validacion = {
            "Descripción": llanta.validacion_descripcion,
            "Serial": llanta.validacion_serial,
            "Quemado": llanta.validacion_quemado,
            "VIN": llanta.validacion_vin,
            "Proveedor": llanta.validacion_proveedor,
            "Fecha": llanta.validacion_fecha_llantas,
            "Documento Anexo": llanta.validacion_documento_anexo,
            "Sello": llanta.validacion_sello,
            "Firma almacén": llanta.validacion_firma_almacen,
            "Firma proveedor": llanta.validacion_firma_proveedor,
        }

        for campo, valor in campos_validacion.items():
            if valor and valor.strip().lower() not in ["correcto", "correcta"]:
                validaciones.append(f"{campo}: {valor.strip()}")

        llanta.validacion_limpia = ', '.join(validaciones) if validaciones else "Sin novedad"

        # Cargar evidencias asociadas con fecha formateada
        evidencias = EvidenciaLlantas.objects.filter(llanta=llanta)
        for evidencia in evidencias:
            evidencia.fecha_formateada = evidencia.fecha.strftime("%d/%m/%Y")
        llanta.evidencias = evidencias

    return render(request, "Tri/listadoLlantas.html", {'llantas': page_obj})


@login_required
def listadoValidacionesManuales(request):
    tris_qs = ValidacionManual.objects.all().order_by("-id")
    paginator = Paginator(tris_qs, 20)  # 20 registros por página
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # Procesar validaciones de cada registro
    for tri in page_obj:
        validaciones = []
        campos_validacion = {
            "Motivo Retiro": tri.motivo_retiro,
            "Sello": tri.validacion_sello,
            "Tachones Enmendaduras": tri.validacion_tachones_enmendaduras,
            "Firma almacén": tri.validacion_firma_almacen,
            "Firma autorización": tri.validacion_firma_autorizacion,
            "Firma proveedor": tri.validacion_firma_proveedor,
        }

        for campo, valor in campos_validacion.items():
            if valor and valor.strip().lower() not in ["correcto", "correcta"]:
                validaciones.append(f"{campo}: {valor.strip()}")

        tri.validacion_limpia = ', '.join(validaciones) if validaciones else "Sin novedad"

    return render(request, "Tri/listadoManuales.html", {
        'tris': page_obj
    })



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



def filtrarConsecutivo(request):
    filtro = request.GET.get('filtro', '').strip()

    if filtro:
        tris = ValidacionTri.objects.filter(consecutivo__icontains=filtro).order_by('-fecha')
    else:
        tris = ValidacionTri.objects.all().order_by('-fecha')

    datos = []
    for tri in tris:
        validaciones = [v.strip() for v in tri.validacion.split(',') if v.strip() and "Correcto" not in v and "Correcta" not in v]
        tri.validacion_limpia = ', '.join(validaciones) if validaciones else "Sin novedad"
        datos.append({
            'id': tri.id,
            'fecha': tri.fecha.strftime('%Y-%m-%d'),
            'hora': tri.hora.strftime('%H:%M:%S'),
            'consecutivo': tri.consecutivo,
            'referencia': tri.referencia,
            'descripcion': tri.descripcion,
            'cantidad': tri.cantidad,
            'unidadMedida': tri.unidad_medida,
            'bodega': tri.bodega,
            'extension': tri.extension,
            'ubicacion': tri.ubicacion,
            'validacion_limpia': tri.validacion_limpia,  
            'vigilante': tri.vigilante.first_name,
        })
    return JsonResponse({'resultados': datos})



def filtrarConsecutivoLlantas(request):
    filtro = request.GET.get('filtro', '').strip()

    if filtro:
        tris = ValidacionLlantas.objects.filter(consecutivo__icontains=filtro).order_by('-fecha')
    else:
        tris = ValidacionLlantas.objects.all().order_by('-fecha')

    datos = []
    for tri in tris:
        validaciones = [v.strip() for v in tri.validacion.split(',') if v.strip() and "Correcto" not in v and "Correcta" not in v]
        tri.validacion_limpia = ', '.join(validaciones) if validaciones else "Sin novedad"
        datos.append({
            'id': tri.id,
            'fecha': tri.fecha.strftime('%Y-%m-%d'),
            'hora': tri.hora.strftime('%H:%M:%S'),
            'consecutivo': tri.consecutivo,
            'referencia': tri.referencia,
            'descripcion': tri.descripcion,
            'serial': tri.serial,
            'quemado': tri.quemado,
            'vin': tri.vin,
            'bodega': tri.bodega,
            'extension': tri.extension,
            'ubicacion': tri.ubicacion,
            'validacion_limpia': tri.validacion_limpia,  
            'vigilante': tri.vigilante.first_name,
        })
    return JsonResponse({'resultados': datos})