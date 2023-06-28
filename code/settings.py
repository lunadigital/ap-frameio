import anchorpoint as ap
import apsync as aps

ctx = ap.get_context()
settings = aps.SharedSettings(ctx.workspace_id, "Frameio")

token_var = ""

def button_clicked(dialog):
    token = dialog.get_value(token_var)
    settings.set("token", token)
    settings.store()
    dialog.close()

def open_dialog():
    token = settings.get("token", "")

    dialog = ap.Dialog()
    dialog.title = "Frame.io Settings"
    dialog.add_text("API Token \t").add_input(token, var=token_var)
    dialog.add_button("Apply", callback=button_clicked)

    if ctx.icon:
        dialog.icon = ctx.icon
    
    dialog.show()

open_dialog()