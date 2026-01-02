# l/memory/shared/error_translator.py


def translate_supabase_error(error_obj):
    """Translate raw Supabase errors into clean internal error structures."""
    if not error_obj:
        return None

    msg = error_obj.get("message", "Unknown")
    code = error_obj.get("code", "UNSPECIFIED")

    return {
        "error": True,
        "type": "SupabaseError",
        "message": msg,
        "code": code,
    }
