import SmartHome as gen
import sys
import Ice
import os

# Proxies info --------------------------------------------------------------------

devices_proxies = {
    "furnace" : (gen.FurnacePrx, "Furnace.Proxy"),
    "chimney_furnace" : (gen.ChimneyFurnacePrx, "ChimneyFurnace.Proxy"),
    "smelting_furnace" : (gen.SmeltingFurnacePrx, "SmeltingFurnace.Proxy"),
    "sensor" : (gen.CarbonSensorPrx, "CarbonSensor.Proxy"),
    "bulbulator" : (gen.BulbulatorPrx, "Bulbulator.Proxy"),
    "advanced_bulbulator" : (gen.AdvancedBulbulatorPrx, "AdvancedBulbulator.Proxy"),
    "furnace_1" : (gen.FurnacePrx, "Furnace1.Proxy"),
    "chimney_furnace_1" : (gen.ChimneyFurnacePrx, "ChimneyFurnace1.Proxy"),
    "chimney_furnace_2" : (gen.ChimneyFurnacePrx, "ChimneyFurnace2.Proxy"),
    "chimney_furnace_3" : (gen.ChimneyFurnacePrx, "ChimneyFurnace3.Proxy"),
}

# Small functions -----------------------------------------------------------------

def print_available_devices(devices):
    print("Available devices : ", end = "")
    print(", ".join(devices.keys()))

def handle_chimney_furnace_callback(future):
    try:
        future.result()
    except gen.CurrentlyChangingState:
        print("Chimney is now changing state.")       

def handle_smelting_furnace_callback(future):
    try:
        future.result()
    except gen.CurrentlySmelting:
        print("Furnace is currenlty smelting.")
    except gen.NoMaterials:
        print("No materials to smelt.")

# Program --------------------------------------------------------------------------

with Ice.initialize(sys.argv) as communicator:
    # Inicialization
    devices = dict()
    for name, proxy in devices_proxies.items():
        base = communicator.propertyToProxy(proxy[1])
        object = proxy[0].checkedCast(base)
        if not object: raise RuntimeError(f"Invalid proxy for {name}.")
        devices[name] = object

    print_available_devices(devices)

    # Client interface
    while True: 
        try:
            command = input("> ").split(" ")
        except:
            raise RuntimeError("Wrong input.")

        if len(command) == 0: 
            continue
        elif command[0] in ["q", "quit", "exit", "stop", "end"]:
            break
        elif command[0] in ["cls", "clear"]:
            os.system("cls")
            print_available_devices(devices)
            continue
        elif command[0] == "":
            continue
        elif len(command) == 1:
            print("Invalid command.")
            continue
        elif command[0] not in devices.keys():
            print("Invalid device name.")
            continue

        device = devices[command[0]]

        if command[1] == "status":
            print(device.logStatus())
            continue
        
        if command[0] in ["furnace", "furnace_1"]:
            match command[1]:
                case "on":
                    device.turnOn()
                    print(device.logStatus())
                    continue
                case "off":
                    device.turnOff()
                    print(device.logStatus())
                    continue
                case "is_on":
                    print(device.isTurnedOn())
                    continue
                case _:
                    print("Wrong command.")
             
        elif command[0] in ["chimney_furnace", "chimney_furnace_1", "chimney_furnace_2", "chimney_furnace_3"]:
            match command[1]:
                case "on":
                    device.turnOn()
                    print(device.logStatus())
                    continue
                case "off":
                    device.turnOff()
                    print(device.logStatus())
                    continue
                case "is_on":
                    print(device.isTurnedOn())
                    continue
                case "chimney_state":
                    print(device.getChimneyState())
                    continue
                case "open":
                    try:
                        device.openChimney()
                        print(device.logStatus())
                    except gen.CurrentlyChangingState:
                        print("Chimney is now changing state.")        
                    continue
                case "open_async":
                    device.openChimneyAsync().add_done_callback(handle_chimney_furnace_callback)  
                    continue
                case "close":
                    try:
                        device.closeChimney()
                        print(device.logStatus())
                    except gen.CurrentlyChangingState:
                        print("Chimney is now changing state.")        
                    continue
                case "close_async":
                    device.closeChimneyAsync().add_done_callback(handle_chimney_furnace_callback)
                    continue
                case _:
                    print("Wrong command.")

        elif command[0] == "smelting_furnace":
            match command[1]:
                case "on":
                    try:
                        device.turnOn()
                        print(device.logStatus())
                    except gen.CurrentlySmelting:
                        print("Furnace is currenlty smelting.")
                    except gen.NoMaterials:
                        print("No materials to smelt.")
                    continue
                case "on_async":
                    device.turnOnAsync().add_done_callback(handle_smelting_furnace_callback)
                    continue
                case "is_on":
                    print(device.isTurnedOn())
                    continue
                case "put": 
                    if len(command) == 2:
                        print("No materials to put.")
                        continue
                    try:
                        device.putMaterials(command[2:])
                    except gen.WrongInput as e:
                        print("Wrong input", e, ".")
                        continue
                    except gen.CurrentlySmelting:
                        print("Cant't put materials while smelting.")
                        continue
                    continue
                case "get":
                    try:
                        print(device.getBackMaterials())
                    except gen.NoMaterials:
                        print("No materials to get back.")
                        continue
                    except gen.CurrentlySmelting:
                        print("Cant't get materials while smelting.")
                        continue
                    continue
                case _:
                    print("Wrong command.")

        elif command[0] == "sensor":
            match command[1]:
                case "check":
                    print(device.checkCarbonMonoxideValue())
                    continue
                case "air_good":     
                    print(device.isAirQualityGood())
                    continue
                case _:
                    print("Wrong command.")

        elif command[0] == "bulbulator":
            match command[1]:
                case "on":
                    try:
                        device.turnOn()
                        print(device.logStatus())
                    except gen.NoBubbleSet:
                        print("No bubble is currently set.")
                        continue
                    continue
                case "off":
                    device.turnOff()
                    print(device.logStatus())
                    continue
                case "is_on":
                    print(device.isTurnedOn())
                    continue
                case "set":
                    if len(command) == 2:
                        print("Wrong input.")
                        continue
                    t = command[2].split("_")    
                    if len(t) != 2:
                        print("Wrong input.")
                        continue
                    size = int(t[1])
                    if size < 1 or size > 127:
                        print("Wrong size.")
                        continue
                    bubble = gen.Bubble()
                    bubble.color = t[0]
                    bubble.size = size
                    try:
                        device.setBubble(bubble)
                        print(device.logStatus())
                    except gen.WrongInput as e:
                        print("Wrong input", e, ".")
                        continue
                    continue
                case "get":
                    try:
                        bubble = device.getCurrentBubble()
                        print("Current bubble : " + bubble.color + " size " + str(bubble.size) + ".")
                        continue
                    except gen.NoBubbleSet:
                        print("No bubble is currently set.")
                        continue
                case _:
                    print("Wrong command.")

        elif command[0] == "advanced_bulbulator":
            match command[1]:
                case "next":
                    try:
                        device.nextBubble()
                        print(device.logStatus())
                    except gen.NoBubbleSet:
                        print("No bubbles are currently set.")
                        continue
                    continue
                case "random":
                    try:
                        device.randomBubble()
                        print(device.logStatus())
                    except gen.NoBubbleSet:
                        print("No bubbles are currently set.")
                        continue
                case "set":
                    if len(command) == 2:
                        print("Wrong input.")
                        continue
                    bubbles = []
                    for x in command[2:]:
                        t = x.split("_")    
                        if len(t) != 2:
                            print("Wrong input.")
                            continue
                        size = int(t[1])
                        if size < 1 or size > 127:
                            print("Wrong size.")
                            continue
                        bubble = gen.Bubble()
                        bubble.color = t[0]
                        bubble.size = size
                        bubbles.append(bubble)
                    try:
                        device.setBubblesSequence(bubbles)
                        print(device.logStatus())
                    except gen.WrongInput as e:
                        print("Wrong input", e, ".")
                        continue
                    continue
                case "get":
                    try:
                        bubble = device.getCurrentBubble()
                        print("Current bubble : " + bubble.color + " size " + str(bubble.size) + ".")
                        continue
                    except gen.NoBubbleSet:
                        print("No bubble is currently set.")
                        continue
                case _:
                    print("Wrong command.")
