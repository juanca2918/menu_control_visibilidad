# -*- coding: utf-8 -*-

def migrate(cr, version):
    """
    Migración para v18.0.3.4.0: Actualizar registros antiguos con config_id
    """
    # Buscar todos los registros de user.menu.visibility que no tienen config_id
    cr.execute("""
        SELECT id, user_id 
        FROM user_menu_visibility 
        WHERE config_id IS NULL
    """)
    
    old_records = cr.fetchall()
    
    if not old_records:
        return
    
    print(f"[user_menu_visibility] Migrando {len(old_records)} registros antiguos...")
    
    for record_id, user_id in old_records:
        if not user_id:
            # Si no tiene user_id, eliminar el registro
            cr.execute("DELETE FROM user_menu_visibility WHERE id = %s", (record_id,))
            continue
        
        # Buscar o crear user.visibility.config para este usuario
        cr.execute("""
            SELECT id FROM user_visibility_config 
            WHERE user_id = %s 
            LIMIT 1
        """, (user_id,))
        
        config_result = cr.fetchone()
        
        if config_result:
            config_id = config_result[0]
        else:
            # Crear configuración para este usuario
            cr.execute("""
                INSERT INTO user_visibility_config (user_id, active, create_date, write_date, create_uid, write_uid)
                VALUES (%s, TRUE, NOW(), NOW(), 1, 1)
                RETURNING id
            """, (user_id,))
            config_id = cr.fetchone()[0]
        
        # Actualizar el registro con el config_id correcto
        cr.execute("""
            UPDATE user_menu_visibility 
            SET config_id = %s 
            WHERE id = %s
        """, (config_id, record_id))
    
    print(f"[user_menu_visibility] Migración completada. {len(old_records)} registros actualizados.")
