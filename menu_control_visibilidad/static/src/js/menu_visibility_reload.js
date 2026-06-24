/** @odoo-module **/

import { ListController } from "@web/views/list/list_controller";
import { patch } from "@web/core/utils/patch";

console.log("User Menu Visibility - Auto reload patch cargado");

patch(ListController.prototype, {
    /**
     * Setup - Configurar listeners de forma segura
     */
    setup() {
        super.setup(...arguments);
        
        // Solo aplicar para user.menu.visibility
        if (this.props.resModel === 'user.menu.visibility') {
            console.log("Aplicando patch de auto-recarga para user.menu.visibility");
            this._menuVisibilityPatched = true;
        }
    },

    /**
     * Override después de actualizar un registro para recargar
     */
    async onWillSaveRecord(record, changes) {
        await super.onWillSaveRecord(...arguments);
        
        // Si es user.menu.visibility y se cambió el campo visible, recargar
        if (this._menuVisibilityPatched && changes && 'visible' in changes) {
            console.log("Campo 'visible' cambiado, programando recarga...");
            setTimeout(async () => {
                try {
                    console.log("Recargando vista...");
                    if (this.model && this.model.root) {
                        await this.model.root.load();
                        console.log("Vista recargada exitosamente");
                    }
                } catch (e) {
                    console.error('Error recargando vista:', e);
                }
            }, 600);
        }
    },
});
