frappe.ui.form.on("Letters Campaign", {
    refresh(frm) {
        frm.add_custom_button(__("Open in Letters Builder"), () => {
            const path = frm.is_new()
                ? "/app/letters-builder"
                : `/app/letters-builder?name=${encodeURIComponent(frm.doc.name)}`;
            window.open(path, "_blank");
        });
    },
});

// Override the list view "New" button to go straight to the builder
// (which shows the template picker instead of the blank Frappe form).
frappe.listview_settings["Letters Campaign"] = {
    onload(listview) {
        listview.page.set_primary_action(__("New Campaign"), () => {
            window.open("/app/letters-builder", "_blank");
        }, "plus");
    },
};
