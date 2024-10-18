import i18n

def configure_i18n():
    i18n.load_path.append('translations')
    i18n.set('filename_format', '{locale}.{format}')
    i18n.set('file_format', 'json')
    i18n.set('skip_locale_root_data', True)
    i18n.set('fallback', 'en')
    i18n.set('enable_memoization', True)

def get_translation(language_code, message_path, **kwargs):
    return i18n.t(message_path, locale=language_code, **kwargs)
