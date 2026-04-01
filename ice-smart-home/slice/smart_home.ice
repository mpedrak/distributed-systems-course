
#ifndef SMART_HOME_ICE
#define SMART_HOME_ICE

module SmartHome
{
	/* Device -------------------------------------------------- */
	
	interface Device
	{
		idempotent string logStatus();
	};

	exception WrongInput { string info; };


	
	/* Furnaces ----------------------------------------------- */
	
	interface Furnace extends Device
	{
		idempotent void turnOn();
		idempotent void turnOff();
		idempotent bool isTurnedOn();		
	};

	exception CurrentlyChangingState {};
	enum ChimneyState { Opened, Closed, Changing };
	
	interface ChimneyFurnace extends Furnace 
	{
		void openChimney() throws CurrentlyChangingState;
		void closeChimney() throws CurrentlyChangingState;
		ChimneyState getChimneyState();	
	};

	sequence<string> Materials;
	exception NoMaterials {};
	exception CurrentlySmelting {};
	
	interface SmeltingFurnace extends Device
	{
		void putMaterials(Materials materials) throws WrongInput, CurrentlySmelting; 
		void turnOn() throws CurrentlySmelting, NoMaterials;
		bool isTurnedOn();	
		Materials getBackMaterials() throws NoMaterials, CurrentlySmelting; 	
	};



	/* Bulbulators -------------------------------------------- */

	struct Bubble
	{
		string color;
		byte size;
	}
	exception NoBubbleSet {};

	interface Bulbulator extends Device
	{
		idempotent void turnOn() throws NoBubbleSet;
		idempotent void turnOff();
		idempotent void setBubble(Bubble bubble) throws WrongInput;
		idempotent bool isTurnedOn();	
		idempotent Bubble getCurrentBubble() throws NoBubbleSet;
	};

	sequence<Bubble> Bubbles;

	interface AdvancedBulbulator extends Device
	{
		idempotent void setBubblesSequence(Bubbles bubbles) throws WrongInput;
		idempotent Bubble getCurrentBubble() throws NoBubbleSet;
		void nextBubble() throws NoBubbleSet;
		void randomBubble() throws NoBubbleSet;
	};



	/* Sensor ------------------------------------------------- */

	interface CarbonSensor extends Device
	{
		int checkCarbonMonoxideValue();
		idempotent bool isAirQualityGood();
	};
};

#endif
