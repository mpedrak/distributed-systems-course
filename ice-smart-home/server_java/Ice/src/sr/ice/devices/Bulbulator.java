package sr.ice.devices;

import SmartHome.Bubble;
import SmartHome.NoBubbleSet;
import SmartHome.WrongInput;
import com.zeroc.Ice.Current;

public class Bulbulator implements SmartHome.Bulbulator
{
    private boolean isOn = false;
    private Bubble currentBubble = null;

    @Override
    public void turnOn(Current current) throws NoBubbleSet
    {
        if (currentBubble == null) throw new NoBubbleSet();
        isOn = true;
    }

    @Override
    public void turnOff(Current current)
    {
        isOn = false;
    }

    @Override
    public void setBubble(Bubble bubble, Current current) throws WrongInput
    {
        if (bubble == null || bubble.color == null || bubble.size < 1) throw new WrongInput("Wrong bubble specs.");
        currentBubble = bubble;
    }

    @Override
    public boolean isTurnedOn(Current current)
    {
        return isOn;
    }

    @Override
    public Bubble getCurrentBubble(Current current) throws NoBubbleSet
    {
        if (currentBubble == null) throw new NoBubbleSet();
        return currentBubble;
    }

    @Override
    public String logStatus(Current current)
    {
        if (currentBubble != null)
            return "Bulbulator - is on : " + isOn + ", current bubble : " + currentBubble.color + " size " + currentBubble.size + ".";
        return "Bulbulator - is on : " + isOn + ", no bubble set.";

    }
}
