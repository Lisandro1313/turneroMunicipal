from typing import Optional
from flask import current_app

def normalize_area(nombre: str) -> tuple[str, str, Optional[str]]:
    """Normaliza un nombre de área a (key, nombre_amigable, piso)
    Usa Config.AREA_VARIANTS_MAP y Config.AREAS_MUNICIPALES_NORMALIZADAS.
    """
    if not nombre:
        return ('DESCONOCIDO', 'Área desconocida', None)

    n = nombre.strip()
    # Intentar mapear variantes
    variants = getattr(current_app.config, 'AREA_VARIANTS_MAP', {})
    key = variants.get(n)
    if not key:
        # Intentar case-insensitive
        for k, v in variants.items():
            if k.lower() == n.lower():
                key = v
                break

    # Si no se encontró, intentar por coincidencia parcial
    if not key:
        lowered = n.lower()
        for k, v in variants.items():
            if lowered in k.lower() or k.lower() in lowered:
                key = v
                break

    # Buscar detalles en catálogo
    catalog = getattr(current_app.config, 'AREAS_MUNICIPALES_NORMALIZADAS', [])
    area = None
    if key:
        area = next((a for a in catalog if a['key'] == key), None)

    # Fallback si no se encuentra
    if not area:
        # Heurísticas simples
        if 'politi' in lowered and 'aliment' in lowered:
            key = 'POLITICAS_ALIMENTARIAS'
        elif 'emerg' in lowered or 'critica' in lowered:
            key = 'EMERGENCIA_ASISTENCIA_CRITICA'
        elif 'calle' in lowered:
            key = 'SITUACION_DE_CALLE'
        elif 'niñez' in lowered or 'adolesc' in lowered:
            key = 'NINEZ_Y_ADOLESCENCIA'
        elif 'integracion' in lowered:
            key = 'INTEGRACION_SOCIAL'
        elif 'articulacion' in lowered:
            key = 'ARTICULACION_OPERATIVA'
        elif 'inclusion' in lowered:
            key = 'INCLUSION_SOCIAL'
        elif 'trabajo social' in lowered:
            key = 'TRABAJO_SOCIAL'
        area = next((a for a in catalog if a['key'] == key), None)

    if area:
        return (area['key'], area['nombre'], area.get('piso'))
    return ('DESCONOCIDO', n, None)

def normalize_motive(texto: str | None) -> tuple[Optional[str], str]:
    """Normaliza motivo libre a (motivo_key, motivo_texto) usando Config.MOTIVO_VARIANTS_MAP"""
    if not texto:
        return (None, '')
    t = texto.strip()
    variants = getattr(current_app.config, 'MOTIVO_VARIANTS_MAP', {})
    key = variants.get(t)
    if not key:
        for k, v in variants.items():
            if k.lower() == t.lower():
                key = v
                break
    if not key:
        l = t.lower()
        if 'materia' in l:
            key = 'MATERIALES'
        elif 'documen' in l or 'planilla' in l:
            key = 'DOCUMENTACION'
        elif 'incend' in l:
            key = 'INCENDIO'
        elif 'tarjeta' in l:
            key = 'TARJETA'
        elif 'comedor' in l:
            key = 'COMEDOR'
        elif 'reun' in l:
            key = 'REUNION'
        elif 'vida' in l and 'mas' in l:
            key = 'PLAN_MAS_VIDA'
        elif 'habitac' in l:
            key = 'HABITACIONAL'
        elif 'recla' in l:
            key = 'RECLAMO'
        elif 'consult' in l:
            key = 'CONSULTA_GENERAL'
    return (key, t)
