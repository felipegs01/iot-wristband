using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Text;
using System.Windows.Forms;
using System.IO.Ports;

namespace IntelEdisonWristbandBluetooth
{
    public partial class frmMain : Form
    {
        private SerialPort comPort = new SerialPort();
        string transType = string.Empty;
        public frmMain()
        {
            InitializeComponent();
            comPort.DataReceived += new SerialDataReceivedEventHandler(comPort_DataReceived);
        }

        private void frmMain_Load(object sender, EventArgs e)
        {
            foreach (string str in SerialPort.GetPortNames())
                cboPort.Items.Add(str.Length > 5 ? str.Substring(0, 5) : str);
            cboPort.SelectedIndex = 0;
            cmdOpen.Enabled = true;
            cmdClose.Enabled = false;
        }

        private void cmdOpen_Click(object sender, EventArgs e)
        {
            try
            {
                //first check if the port is already open
                if (comPort.IsOpen == true) comPort.Close();

                //set the properties of our SerialPort Object
                comPort.BaudRate = 9600;
                comPort.StopBits = StopBits.One;
                comPort.Parity = Parity.None;
                comPort.PortName = cboPort.Text;
                comPort.Open();
                printLog("Serial Port " + cboPort.Text + " open");

                cmdOpen.Enabled = false;
                cmdClose.Enabled = true;
            }
            catch (Exception ex)
            {
                printLog(ex.Message);
            }
        }

        private void cmdClose_Click(object sender, EventArgs e)
        {
            if (comPort.IsOpen == true) comPort.Close();
            cmdOpen.Enabled = true;
            cmdClose.Enabled = false;
            printLog("Serial Port " + cboPort.Text + " closed");
        }

        [STAThread]
        private void printLog(string msg)
        {
            rtbDisplay.Invoke(new EventHandler(delegate
            {
                rtbDisplay.SelectedText = string.Empty;
                rtbDisplay.AppendText(msg);
                rtbDisplay.ScrollToCaret();
            }));
        }

        void comPort_DataReceived(object sender, SerialDataReceivedEventArgs e)
        {
            string msg = comPort.ReadExisting();
            printLog("Received: " + msg + "\n");
            processMessage(msg);
        }

        void processMessage(string msg)
        {
            switch (msg)
            {
                case "right": SendKeys.SendWait("N"); break;
                case "left": SendKeys.SendWait("P"); break;
                case "up": SendKeys.SendWait("{F5}"); break;
            }
        }
    }
}