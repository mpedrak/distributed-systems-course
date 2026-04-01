package sr.ice.server;

import com.zeroc.Ice.Communicator;
import com.zeroc.Ice.Identity;
import com.zeroc.Ice.ObjectAdapter;
import com.zeroc.Ice.Util;
import sr.ice.devices.*;

public class IceServer
{
	public void t1(String[] args)
	{
		int status = 0;
		Communicator communicator = null;

		try
		{
			communicator = Util.initialize(args);
			ObjectAdapter adapter = communicator.createObjectAdapter("Adapter1");

			if (args[0].endsWith("2"))
			{
				System.out.println("Server 2");
				adapter.add(new Furnace(), new Identity("furnace_1", "device"));
				adapter.add(new ChimneyFurnace(), new Identity("chimney_furnace_1", "device"));
				adapter.add(new ChimneyFurnace(), new Identity("chimney_furnace_2", "device"));
				adapter.add(new ChimneyFurnace(), new Identity("chimney_furnace_3", "device"));
			}
			else
			{
				System.out.println("Server 1");
				adapter.add(new Furnace(), new Identity("furnace", "device"));
				adapter.add(new ChimneyFurnace(), new Identity("chimney_furnace", "device"));
				adapter.add(new SmeltingFurnace(), new Identity("smelting_furnace", "device"));
				adapter.add(new CarbonSensor(), new Identity("carbon_sensor", "device"));
				adapter.add(new Bulbulator(), new Identity("bulbulator", "device"));
				adapter.add(new AdvancedBulbulator(), new Identity("advanced_bulbulator", "device"));
			}

			adapter.activate();
			System.out.println("Entered event processing loop.");
			communicator.waitForShutdown();
		}
		catch (Exception e)
		{
			e.printStackTrace(System.err);
			status = 1;
		}
		if (communicator != null) {
			try
			{
				communicator.destroy();
			}
			catch (Exception e)
			{
				e.printStackTrace(System.err);
				status = 1;
			}
		}
		System.exit(status);
	}


	public static void main(String[] args)
	{
		IceServer app = new IceServer();
		app.t1(args);
	}
}