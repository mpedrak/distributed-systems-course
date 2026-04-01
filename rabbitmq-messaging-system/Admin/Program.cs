using RabbitMQ.Client.Events;
using RabbitMQ.Client;
using System.Text;

namespace Admin
{
    class Program
    {
        static void Main(string[] args)
        {
            Console.WriteLine("Admin started.");

            var factory = new ConnectionFactory { HostName = "localhost" };
            using var connection = factory.CreateConnection();
            using var channel = connection.CreateModel();

            channel.QueueDeclare("admin_queue", false, false, false, null);

            channel.ExchangeDeclare("order_exchange", ExchangeType.Direct);         
            channel.QueueBind("admin_queue", "order_exchange", "knee");
            channel.QueueBind("admin_queue", "order_exchange", "elbow");
            channel.QueueBind("admin_queue", "order_exchange", "hip");

            channel.ExchangeDeclare("result_exchange", ExchangeType.Direct);                 
            var medic_queues = new HashSet<string>();

            var log_handler = new EventingBasicConsumer(channel);
            log_handler.Received += (model, body) =>
            {
                var message = Encoding.UTF8.GetString(body.Body.ToArray());
                if (body.Exchange.Equals("order_exchange"))
                {
                    var message_parts = message.Split(' ');
                    if (!medic_queues.Contains(message_parts[1])) 
                    {
                        medic_queues.Add(message_parts[1]);
                        channel.QueueBind("admin_queue", "result_exchange", message_parts[1]);
                    }
                }
                Console.WriteLine("\r" + body.RoutingKey + " " + message);
            };

            channel.BasicConsume("admin_queue", true, log_handler);
            Console.WriteLine("Started printing logs.");

            channel.ExchangeDeclare("info_exchange", ExchangeType.Topic);
            Console.WriteLine("To send message : info <all/medic/tech/tech.<knee/elbow/hip>> <message>, to end - exit");

            while (true)
            {
                var line = Console.ReadLine();
                if (line == null)
                {
                    Console.WriteLine("Wrong input.");
                    continue;
                }
                if (line.Equals("exit")) break;

                var words = line.Split(' ');
                if (words.Length < 3)
                {
                    Console.WriteLine("Wrong amount of words.");
                    continue;
                }
                if (words[0] != "info")
                {
                    Console.WriteLine("Wrong command.");
                    continue;
                }
                if (words[1].Length < 1 || (words[1] != "all" && words[1] != "medic" && words[1] != "tech"
                    && words[1] != "tech.knee" && words[1] != "tech.elbow" && words[1] != "tech.hip"))
                {
                    Console.WriteLine("Wrong receiver.");
                    continue;
                }
                if (words[2].Length < 1)
                {
                    Console.WriteLine("Wrong message.");
                    continue;
                }
                StringBuilder stringBuilder = new StringBuilder();
                for (int i = 2; i < words.Length; i++) stringBuilder.Append(words[i] + " ");
                channel.BasicPublish("info_exchange", words[1], null, Encoding.UTF8.GetBytes("info from admin - " + stringBuilder.ToString()));
            }
            Console.WriteLine("Admin stopped.");
        }
    }
}
