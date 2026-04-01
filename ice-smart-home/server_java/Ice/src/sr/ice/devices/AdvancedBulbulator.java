package sr.ice.devices;

import SmartHome.Bubble;
import SmartHome.NoBubbleSet;
import SmartHome.WrongInput;
import com.zeroc.Ice.Current;

import java.util.Random;

public class AdvancedBulbulator implements SmartHome.AdvancedBulbulator
{
    private Bubble[] bubbles = null;
    private int current_idx = 0;
    private Random random = new Random();

    @Override
    public void setBubblesSequence(Bubble[] bubbles, Current current) throws WrongInput
    {
        if (bubbles == null || bubbles.length == 0) throw new WrongInput("Wrong bubble sequence.");
        for (Bubble bubble : bubbles)
            if (bubble == null || bubble.color == null || bubble.size < 1) throw new WrongInput("Wrong bubble specs.");
        this.bubbles = bubbles;
    }

    @Override
    public Bubble getCurrentBubble(Current current) throws NoBubbleSet
    {
        if (bubbles == null) throw new NoBubbleSet();
        return bubbles[current_idx];
    }

    @Override
    public void nextBubble(Current current) throws NoBubbleSet
    {
        if (bubbles == null) throw new NoBubbleSet();
        current_idx = (current_idx + 1) % bubbles.length;
    }

    @Override
    public void randomBubble(Current current) throws NoBubbleSet
    {
        if (bubbles == null) throw new NoBubbleSet();
        current_idx = random.nextInt(bubbles.length);
    }

    @Override
    public String logStatus(Current current)
    {
        if (bubbles == null) return "Advanced Bulbulator - no bubbles sequence is set.";
        StringBuilder text =  new StringBuilder("Advanced Bulbulator - current bubble index : " + current_idx + ", bubble sequence : [");
        for (Bubble bubble : bubbles) text.append(bubble.color).append(" size ").append(bubble.size).append(", ");
        String t = text.substring(0, text.length() - 2);
        t += "].";
        return t;
    }
}
