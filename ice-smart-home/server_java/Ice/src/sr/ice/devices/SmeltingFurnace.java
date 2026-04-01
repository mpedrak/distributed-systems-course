package sr.ice.devices;

import SmartHome.CurrentlySmelting;
import SmartHome.NoMaterials;
import SmartHome.WrongInput;
import com.zeroc.Ice.Current;

import java.util.Arrays;

public class SmeltingFurnace implements SmartHome.SmeltingFurnace
{
    private String[] materials = null;
    private boolean isOn = false;

    @Override
    public String logStatus(Current current)
    {
        return "Smelting furnace is on : " + isOn + ", materials : " + Arrays.toString(materials) + ".";
    }

    @Override
    public void putMaterials(String[] materials, Current current) throws CurrentlySmelting, WrongInput
    {
        if (materials == null || materials.length == 0) throw new WrongInput("Wrong materials sequence.");
        else if (isOn) throw new CurrentlySmelting();
        else this.materials = materials;
    }

    @Override
    public void turnOn(Current current) throws CurrentlySmelting, NoMaterials
    {
        if (materials == null) throw new NoMaterials();
        else if (isOn) throw new CurrentlySmelting();
        else
        {
            isOn = true;
            try { Thread.sleep(7000); } catch (InterruptedException e) { System.out.println(e.getMessage()); }
            String[] smeltedMaterials = new String[materials.length];
            for (int i = 0; i < materials.length; i++) smeltedMaterials[i] = "smelted " + materials[i];
            materials = smeltedMaterials;
            isOn = false;
        }
    }

    @Override
    public boolean isTurnedOn(Current current)
    {
        return isOn;
    }

    @Override
    public String[] getBackMaterials(Current current) throws CurrentlySmelting, NoMaterials
    {
        if (materials == null) throw new NoMaterials();
        else if (isOn) throw new CurrentlySmelting();
        String[] materials_copy = materials.clone();
        materials = null;
        return materials_copy;
    }
}
