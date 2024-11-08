from pythonosc import udp_client

print('osc_client = udp_client.SimpleUDPClient("127.0.0.1",8000)')
osc_client = udp_client.SimpleUDPClient("127.0.0.1",8000)

# print('osc_client.send_message("/sequences/seq2/play", 1)')
# osc_client.send_message("/sequences/seq2/play", 1)

print('/sources/1/restart')
osc_client.send_message("/sources/1/restart", 1)