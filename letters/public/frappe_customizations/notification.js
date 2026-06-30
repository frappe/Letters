frappe.ui.form.on("Notification", {
	refresh(frm) {
		if (frm.doc.letter) {
			frm.add_custom_button(__("Open Letter"), () => {
				window.open(`/app/letter-builder/${frm.doc.letter}?tab=notifications`, "_blank");
			}, __("Letters"));
		} else {
			frm.add_custom_button(__("Design with Letters"), async () => {
				if (frm.is_new()) {
					frappe.msgprint(__("Please save the notification first, then use Design with Letters."));
					return;
				}
				frm.disable_save();
				try {
					const res = await frappe.call({
						method: "letters.letters.api.notifications.create_letter_for_notification",
						args: { notification: frm.doc.name },
					});
					const letterName = res.message.letter;
					frm.set_value("letter", letterName);
					await frm.save();
					window.open(`/app/letter-builder/${letterName}?tab=notifications`, "_blank");
				} finally {
					frm.enable_save();
				}
			}, __("Letters"));
		}
	},
});
