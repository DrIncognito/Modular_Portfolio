from modular_portfolio.modular_core.interface import BasePlugin
import platform
import subprocess
import sys
import time
import socket

class TestTool(BasePlugin):
    def run(self, mode: str):
        if mode == 'cli':
            self.cli_menu()
        elif mode == 'web':
            from flask import render_template, request
            result = None
            action = request.args.get('action')
            # Use class methods directly for plugin compatibility

            if action == 'speed':
                result = TestTool.speed_test(self, return_output=True)
            elif action == 'sysinfo':
                result = TestTool.system_info(self, return_output=True)
            elif action == 'netinfo':
                result = TestTool.network_info(self, return_output=True)
            return render_template('test_tool.html', result=result)
        elif mode == 'gui':
            self.gui_menu()
        else:
            print(f"Unknown mode: {mode}")

    def cli_menu(self):
        while True:
            print("\n[TestTool CLI]")
            print("1. Speed Test")
            print("2. System Info")
            print("3. Network Info")
            print("4. Exit")
            choice = input("Select a test: ").strip()
            if choice == '1':
                self.speed_test()
            elif choice == '2':
                self.system_info()
            elif choice == '3':
                self.network_info()
            elif choice == '4':
                print("Exiting TestTool.")
                break
            else:
                print("Invalid choice.")

    def speed_test(self, return_output=False):
        import shutil
        import re
        if shutil.which('speedtest'):
            try:
                output = subprocess.check_output(['speedtest', '--simple'], stderr=subprocess.STDOUT, universal_newlines=True)
                # Parse output for Download, Upload, Ping
                download = re.search(r'Download:\s+([\d.]+)\s+Mbit/s', output)
                upload = re.search(r'Upload:\s+([\d.]+)\s+Mbit/s', output)
                ping = re.search(r'Ping:\s+([\d.]+)\s+ms', output)
                msg = []
                if download:
                    msg.append(f"Download: {download.group(1)} Mbps")
                if upload:
                    msg.append(f"Upload: {upload.group(1)} Mbps")
                if ping:
                    msg.append(f"Ping: {ping.group(1)} ms")
                msg = '\n'.join(msg) if msg else output
                if return_output:
                    return msg
                print(msg)
            except Exception as e:
                msg = f"Speedtest failed: {e}"
                if return_output:
                    return msg
                print(msg)
        else:
            msg = "speedtest CLI not found. Please install it with 'sudo apt install speedtest-cli' or 'pip install speedtest-cli' and ensure it's in your PATH."
            if return_output:
                return msg
            print(msg)

    def system_info(self, return_output=False):
        info = [
            f"Platform: {platform.system()} {platform.release()}",
            f"Processor: {platform.processor()}",
            f"Python Version: {platform.python_version()}",
            f"Machine: {platform.machine()}",
            f"Node: {platform.node()}",
            f"Uptime: {self.get_uptime()}"
        ]
        msg = '\n'.join(info)
        if return_output:
            return msg
        print(msg)

    def network_info(self, return_output=False):
        import os
        import re
        info = []
        try:
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            info.append(f"Hostname: {hostname}")
            info.append(f"Local IP: {local_ip}")
            # MAC address (first non-loopback interface)
            mac = None
            if sys.platform.startswith('linux'):
                for iface in os.listdir('/sys/class/net/'):
                    if iface == 'lo':
                        continue
                    try:
                        with open(f'/sys/class/net/{iface}/address') as f:
                            mac = f.read().strip()
                        if mac:
                            info.append(f"MAC Address: {mac}")
                            break
                    except Exception:
                        continue
            # Gateway
            gateway = None
            if sys.platform.startswith('linux'):
                try:
                    with open('/proc/net/route') as f:
                        for line in f.readlines()[1:]:
                            parts = line.split()
                            if parts[1] != '00000000' or not int(parts[3], 16) & 2:
                                continue
                            gateway = socket.inet_ntoa(bytes.fromhex(parts[2])[::-1])
                            info.append(f"Gateway: {gateway}")
                            break
                except Exception:
                    pass
            # DNS servers
            dns = []
            if sys.platform.startswith('linux'):
                try:
                    with open('/etc/resolv.conf') as f:
                        for line in f:
                            if line.startswith('nameserver'):
                                dns.append(line.split()[1])
                    if dns:
                        info.append(f"DNS: {', '.join(dns)}")
                except Exception:
                    pass
        except Exception as e:
            info.append(f"Network info failed: {e}")
        msg = '\n'.join(info)
        if return_output:
            return msg
        print(msg)

    def get_uptime(self):
        if platform.system() == 'Windows':
            try:
                import psutil
                return f"{int(time.time() - psutil.boot_time()) // 60} minutes"
            except ImportError:
                return "psutil not installed"
        else:
            try:
                with open('/proc/uptime', 'r') as f:
                    uptime_seconds = float(f.readline().split()[0])
                    return f"{int(uptime_seconds // 60)} minutes"
            except Exception:
                return "Unknown"

    def gui_menu(self):
        try:
            from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QTextEdit, QLabel
        except ImportError:
            print("PyQt5 is not installed. Please install it to use GUI features.")
            return
        import sys
        app = QApplication.instance() or QApplication(sys.argv)
        window = QMainWindow()
        window.setWindowTitle("TestTool GUI")
        central = QWidget()
        layout = QVBoxLayout()
        label = QLabel("TestTool - Select a test:")
        layout.addWidget(label)
        output = QTextEdit()
        output.setReadOnly(True)
        def run_speed():
            result = self.speed_test(return_output=True)
            output.setText(result)
        def run_sys():
            result = self.system_info(return_output=True)
            output.setText(result)
        def run_net():
            result = self.network_info(return_output=True)
            output.setText(result)
        btn_speed = QPushButton("Speed Test")
        btn_speed.clicked.connect(run_speed)
        btn_sys = QPushButton("System Info")
        btn_sys.clicked.connect(run_sys)
        btn_net = QPushButton("Network Info")
        btn_net.clicked.connect(run_net)
        for btn in [btn_speed, btn_sys, btn_net]:
            layout.addWidget(btn)
        layout.addWidget(output)
        central.setLayout(layout)
        window.setCentralWidget(central)
        window.resize(500, 400)
        window.show()
        app.exec_()
