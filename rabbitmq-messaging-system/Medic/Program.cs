using RabbitMQ.Client.Events;
using RabbitMQ.Client;
using System.Text;

namespace Medic
{
    class Program
    {
        static void Main(string[] args)
        {
            Console.WriteLine("Medic started.");

            var factory = new ConnectionFactory { HostName = "localhost" };
            using var connection = factory.CreateConnection();
            using var channel = connection.CreateModel();
          
            channel.ExchangeDeclare("order_exchange", ExchangeType.Direct);

            channel.ExchangeDeclare("result_exchange", ExchangeType.Direct);
            var result_queue = channel.QueueDeclare();
            string result_queue_name = result_queue.QueueName;
            channel.QueueBind(result_queue_name, "result_exchange", result_queue_name);

            var result_handler = new EventingBasicConsumer(channel);
            result_handler.Received += (model, body) =>
            {
                channel.BasicAck(body.DeliveryTag, false);            
                var message = Encoding.UTF8.GetString(body.Body.ToArray());
                Console.WriteLine("\r> Received : " + message);
            };
        
            channel.ExchangeDeclare("info_exchange", ExchangeType.Topic);
            channel.QueueBind(result_queue_name, "info_exchange", "all");
            channel.QueueBind(result_queue_name, "info_exchange", "medic");
            channel.BasicConsume(result_queue_name, false, result_handler);

            Console.WriteLine("Send order - <knee/elbow/hip> <patient_surname>, to end - exit.");

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
                if (words.Length != 2)
                {
                    Console.WriteLine("Wrong amount of words.");
                    continue;
                }
                if (words[0] != "hip" && words[0] != "knee" && words[0] != "elbow")
                {
                    Console.WriteLine("Wrong probe type.");
                    continue;
                }
                if (words[1].Length < 1)
                {
                    Console.WriteLine("Wrong patient surname.");
                    continue;
                }
                channel.BasicPublish("order_exchange", words[0], null, Encoding.UTF8.GetBytes(words[1] + " " + result_queue_name));
            }
            Console.WriteLine("Medic stopped.");
        }
    }
}