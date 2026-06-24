# -*- coding: utf-8 -*-


def migrate(cr, version):
    """
    v18.0.5.6.0: Eliminar columna can_pay de user_menu_visibility.
    El campo ya no existe en el modelo — la lógica de botones de pago
    queda absorbida por can_write (si puede editar, ve los botones de acción).
    """
    cr.execute("""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name = 'user_menu_visibility'
          AND column_name = 'can_pay'
    """)
    if cr.fetchone():
        cr.execute("ALTER TABLE user_menu_visibility DROP COLUMN can_pay")
