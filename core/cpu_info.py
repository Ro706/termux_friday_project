import psutil

def cpu_info():
    cpu_percent = psutil.cpu_percent(interval=1)
    cpu_freq = psutil.cpu_freq()
    cpu_count = psutil.cpu_count()
    cpu_time = psutil.cpu_times()

    report = f"CPU Usage: {cpu_percent}%\n"
    report += f"CPU Frequency: {cpu_freq.current:.2f}Mhz\n"
    report += f"CPU Cores: {cpu_count}\n"
    report += f"CPU Times: {cpu_time}"
    
    return report

if __name__ == "__main__":
    print(cpu_info())
