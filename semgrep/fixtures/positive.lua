local server_code = matches[2]
load(server_code)
os.execute(server_code)

local server_command = matches[2]
send(server_command)

local server_path = msdp.DOWNLOAD_PATH
io.open(server_path, "w")

tempTimer(1, "send('look')")

local server_markup = matches[2]
GUI.Status:echo(server_markup)

local private_protocol_data = msdp.CHARACTER
GUI.debug("PROTOCOL", private_protocol_data)
