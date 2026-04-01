package sr.ice.devices;

import com.zeroc.Ice.Current;

public class Furnace implements SmartHome.Furnace
{
    protected boolean isOn = false;

    @Override
    public String logStatus(Current current)
    {
        return "Furnace - is on : " + isOn + ".";
    }

    @Override
    public void turnOn(Current current)
    {
        isOn = true;
    }

    @Override
    public void turnOff(Current current)
    {
        isOn = false;
    }

    @Override
    public boolean isTurnedOn(Current current)
    {
        return isOn;
    }
}
