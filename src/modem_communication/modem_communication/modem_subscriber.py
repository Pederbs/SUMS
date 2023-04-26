import rclpy
from rclpy.node import Node
from sensor_interfaces.msg import *
from unetpy import UnetSocket
import time


class ModemSubscriberNode(Node):
    
    def __init__(self):
        super().__init__('modem_subscriber')
        self.sock  = UnetSocket('192.168.42.195', 1100)


        self.publisher_ = self.create_publisher(Modem, 'internal_modem_data', 10)  # Creates a publisher over the topic salinity_data
        self.times_checked = 0
        self.n_sensors  = self.declare_parameter('sensor_count', 5).value  # Gets how many sensors it is expecting values from
        #self.rigg_ID  = self.declare_parameter('rigg_ID', 1).value  # Gets Identification number for the rigg

        # Defining memory variables
        self.barometer_data = {
            'time': '00:00',
            'depth': 0.0,
            'pressure': 0.0
        }
        self.battery_data = {
            'time': '00:00',
            'voltage': 0.0,
            'current': 0.0,
            'percent': 0.0
        }
        self.oxygen_data = {
            'time': '00:00',
            'oxygen': 0.0
        }
        self.salinity_data = {
            'time': '00:00',
            'salinity': 0.0
        }
        self.temperature_data = {
            'time': '00:00',
            'temperature': 0.0
        }

        self.barometer_subscription = self.create_subscription(
            Barometer, 
            '/barometer/barometer_data', 
            self.barometer_callback, 
            10)

        self.battery_subscription = self.create_subscription(
            Battery, 
            '/battery/battery_data', 
            self.battery_callback, 
            10)

        self.oxygen_subscription = self.create_subscription(
            Oxygen, 
            '/oxygen/oxygen_data', 
            self.oxygen_callback, 
            10)

        self.salinity_subscription = self.create_subscription(
            Salinity, 
            '/salinity/salinity_data', 
            self.salinity_callback, 
            10)

        self.temperature_subscription = self.create_subscription(
            Thermometer, 
            '/thermometer/thermometer_data', 
            self.temperature_callback, 
            10)

        #Prevent unused variable warning
        self.barometer_subscription   # Prevent unused variable warning
        self.battery_subscription   # Prevent unused variable warning
        self.oxygen_subscription   # Prevent unused variable warning
        self.salinity_subscription   # Prevent unused variable warning
        self.temperature_subscription   # Prevent unused variable warning


    def send_data_modem(self):
        if self.times_checked >= self.n_sensors:
            # Getting the local time
            current_time = time.localtime()
            #msg.local_time =  time.strftime("%H:%M:%S",current_time) ## Does  not do anything?
            # data = '%i,%s,%0.4f,%0.4f,%0.4f,%0.4f,%0.4f' % (self.rigg_ID, # Handeled by modem
            data = '%s,%0.4f,%0.4f,%0.4f,%0.4f,%0.4f' % (current_time,
                                                         self.barometer_data['depth'],
                                                         self.battery_data['voltage'],
                                                         self.oxygen_data['oxygen'],
                                                         self.salinity_data['salinity'],
                                                         self.temperature_data['temperature'])
            
            modem_msg = Modem()
            modem_msg.internal_data = data
            self.publisher_.publish(modem_msg)
            
            try:
                self.sock.send(data, 0)
                self.get_logger().info('DATA SENT TO MODEM')
            except:
                self.get_logger().error('COULD NOT SEND DATA TO MODEM')
            self.times_checked = 0

    def barometer_callback(self, msg:Barometer):
        self.barometer_data['pressure'] = msg.pressure_mbar
        self.barometer_data['depth'] = msg.depth
        self.barometer_data['time'] = msg.local_time
        #self.get_logger().info('Extracted %0.2f mbar at depth %0.2f  time: %s'% (self.barometer_data['pressure'], 
        #                                                                         self.barometer_data['depth'], 
        #                                                                         self.barometer_data['time']))
        #self.subscribers_updated['barometer_data'] = True
        self.times_checked += 1
        self.send_data_modem()

    def battery_callback (self, msg:Battery):
        self.battery_data['voltage'] = msg.battery_voltage
        self.battery_data['current'] = msg.battery_current
        self.battery_data['percent'] = msg.battery_percent
        self.battery_data['time'] = msg.local_time
        #self.get_logger().info('Extracted %0.2f V and  %0.2f A with %0.2f %  time: %s'% (self.battery_data['voltage'], 
        #                                                                                 self.battery_data['current'], 
        #                                                                                 self.battery_data['percent'], 
        #                                                                                 self.battery_data['time']))
        #self.subscribers_updated['battery_data'] = True
        self.times_checked += 1
        self.send_data_modem()
 
    def oxygen_callback(self, msg:Oxygen):
        self.oxygen_data['oxygen'] = msg._oxygen_concentration
        self.oxygen_data['time'] = msg.local_time
        #self.get_logger().info('Extracted %0.2f O at time: %s'% (self.oxygen_data['oxygen'], 
        #                                                         self.oxygen_data['time']))
        #self.subscribers_updated['oxygen_data'] = True
        self.times_checked += 1
        self.send_data_modem()
 
    def salinity_callback(self, msg:Salinity):
        self.salinity_data['salinity'] = msg.salinity_value
        self.salinity_data['time'] = msg.local_time
        #self.get_logger().info('Extracted %0.2f O at time: %s'% (self.salinity_data['salinity'], 
        #                                                         self.salinity_data['time']))
        #self.subscribers_updated['salinity_data'] = True
        self.times_checked += 1
        self.send_data_modem()
 
    def temperature_callback(self, msg:Thermometer):
        self.temperature_data['temperature'] = msg.temperature_celsius
        self.temperature_data['time'] = msg.local_time
        #self.get_logger().info('Extracted %0.2f C at time: %s'% (self.temperature_data['temperature'], 
        #                                                         self.temperature_data['time']))
        #self.subscribers_updated['thermometer_data'] = True
        self.times_checked += 1
        self.send_data_modem()
        

def main(args=None):
    rclpy.init(args=args)

    modem_subscriber = ModemSubscriberNode()

    rclpy.spin(modem_subscriber)


    modem_subscriber.destroy_node()
    rclpy.shutdown


if __name__ == '__main__':
    main()