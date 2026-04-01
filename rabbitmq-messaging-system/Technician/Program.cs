using RabbitMQ.Client.Events;
using RabbitMQ.Client;
using System.Text;

namespace Technician
{
    class Program
    {
        static void Main(string[] args)
        {
            Console.WriteLine("Technician started.");

            var factory = new ConnectionFactory { HostName = "localhost" };
            using var connection = factory.CreateConnection();
            using var channel = connection.CreateModel();
            channel.BasicQos(0, 1, true);

            var probe_types = new List<string>();

            while (true) 
            {           
                Console.WriteLine("Select 2 types of probe from - hip, knee, elbow.");
                var line = Console.ReadLine();
                if (line == null)
                {
                    Console.WriteLine("Wrong input.\n");
                    continue;
                }               
                var words = line.Split(' ');
                if (words.Length != 2) 
                {
                    Console.WriteLine("Wrong amount of probes.\n");
                    continue;
                }
                if (words[0] != "hip" && words[0] != "knee" && words[0] != "elbow")
                {
                    Console.WriteLine("Wrong first type.\n");
                    continue;
                }
                if (words[1] != "hip" && words[1] != "knee" && words[1] != "elbow")
                {
                    Console.WriteLine("Wrong second type.\n");
                    continue;
                }
                probe_types.Add(words[0]);
                probe_types.Add(words[1]);
                break;
            }

            channel.ExchangeDeclare("order_exchange", ExchangeType.Direct);
            channel.QueueDeclare(probe_types[0], false, false, false, null);
            channel.QueueDeclare(probe_types[1], false, false, false, null);
            channel.QueueBind(probe_types[0], "order_exchange", probe_types[0]);
            channel.QueueBind(probe_types[1], "order_exchange", probe_types[1]);

            channel.ExchangeDeclare("result_exchange", ExchangeType.Direct);
            Random random_generator = new Random();

            var probe_0_handler = new EventingBasicConsumer(channel);
            probe_0_handler.Received += (model, body) =>
            {
                channel.BasicAck(body.DeliveryTag, false);
                var message = Encoding.UTF8.GetString(body.Body.ToArray()).Split(' ');
                Console.WriteLine($"Received {probe_types[0]} order from medic {message[1]} for patient {message[0]}");
                Thread.Sleep(random_generator.Next() % 4000 + 4000);
                channel.BasicPublish("result_exchange", message[1], null, Encoding.UTF8.GetBytes(message[0] + $" {probe_types[0]} done"));
            };

            var probe_1_handler = new EventingBasicConsumer(channel);
            probe_1_handler.Received += (model, body) =>
            {
                channel.BasicAck(body.DeliveryTag, false);
                var message = Encoding.UTF8.GetString(body.Body.ToArray()).Split(' ');
                Console.WriteLine($"Received {probe_types[1]} order from medic {message[1]} for patient {message[0]}");
                Thread.Sleep(random_generator.Next() % 4000 + 4000);
                channel.BasicPublish("result_exchange", message[1], null, Encoding.UTF8.GetBytes(message[0] + $" {probe_types[1]} done"));
            };
 
            channel.BasicConsume(probe_types[0], false, probe_0_handler);
            channel.BasicConsume(probe_types[1], false, probe_1_handler);

            var info_queue = channel.QueueDeclare();
            string info_queue_name = info_queue.QueueName;

            var info_handler = new EventingBasicConsumer(channel);
            info_handler.Received += (model, body) =>
            {
                channel.BasicAck(body.DeliveryTag, false);
                var message = Encoding.UTF8.GetString(body.Body.ToArray());
                Console.WriteLine("\r> Received : " + message);
            };

            channel.ExchangeDeclare("info_exchange", ExchangeType.Topic);
            channel.QueueBind(info_queue_name, "info_exchange", "all");
            channel.QueueBind(info_queue_name, "info_exchange", "tech");
            channel.QueueBind(info_queue_name, "info_exchange", "tech." + probe_types[0]);
            channel.QueueBind(info_queue_name, "info_exchange", "tech." + probe_types[1]);
            channel.BasicConsume(info_queue_name, false, info_handler);

            Console.WriteLine("Waiting for orders, to end - exit.");
            var end = Console.ReadLine();
            while (end != null && !end.Equals("exit")) end = Console.ReadLine();
            Console.WriteLine("Technician stopped.");
        }
    }
}