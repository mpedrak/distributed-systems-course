package sr.ice.devices;

import SmartHome.ChimneyState;
import SmartHome.CurrentlyChangingState;
import com.zeroc.Ice.Current;

public class ChimneyFurnace extends Furnace implements SmartHome.ChimneyFurnace
{
    private ChimneyState chimneyState = ChimneyState.Closed;

    @Override
    public void openChimney(Current current) throws CurrentlyChangingState
    {
        if (chimneyState == ChimneyState.Changing) throw new CurrentlyChangingState();
        else if (chimneyState == ChimneyState.Closed)
        {
            chimneyState = ChimneyState.Changing;
            try { Thread.sleep(7000); } catch (InterruptedException e) { System.out.println(e.getMessage()); }
            chimneyState = ChimneyState.Opened;
        }
    }

    @Override
    public void closeChimney(Current current) throws CurrentlyChangingState
    {
        if (chimneyState == ChimneyState.Changing) throw new CurrentlyChangingState();
        else if (chimneyState == ChimneyState.Opened)
        {
            chimneyState = ChimneyState.Changing;
            try { Thread.sleep(7000); } catch (InterruptedException e) { System.out.println(e.getMessage()); }
            chimneyState = ChimneyState.Closed;
        }
    }

    @Override
    public ChimneyState getChimneyState(Current current)
    {
        return chimneyState;
    }

    @Override
    public String logStatus(Current current)
    {
        return "Chimney furnace - is on : " + isOn + ", chimney state : " + chimneyState + ".";
    }
}
