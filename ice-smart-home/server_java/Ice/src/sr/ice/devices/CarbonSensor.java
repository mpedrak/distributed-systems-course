package sr.ice.devices;

import com.zeroc.Ice.Current;

import java.util.Random;

public class CarbonSensor implements SmartHome.CarbonSensor
{
    private Random random = new Random();
    private int value = random.nextInt(10);
    @Override
    public int checkCarbonMonoxideValue(Current current)
    {
        value = random.nextInt(10);
        return value;
    }

    @Override
    public boolean isAirQualityGood(Current current)
    {
        return value < 7;
    }

    @Override
    public String logStatus(Current current)
    {
        return "Carbon Sensor - carbon monoxide value : " + value + ", air good : " + isAirQualityGood(current) + ".";
    }
}
