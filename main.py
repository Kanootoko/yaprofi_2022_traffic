from typing import Dict, NamedTuple, TextIO
from math import floor, ceil
import click

TrafficMeasure = NamedTuple('TrafficMeasure', (
    ('avg', float),
    ('times', int)
))

class TrafficModel:
    def __init__(self):
        avg = 0
        times = 0
        self.traffic: Dict[int, TrafficMeasure] = {hour: TrafficMeasure(avg, times) for hour in range(24)}
    
    def add_measure(self, time: int, traffic: float) -> None:
        self.traffic[time] = TrafficMeasure(
                (self.traffic[time].avg * self.traffic[time].times + traffic) / (self.traffic[time].times + 1),
                self.traffic[time].times + 1
        )

    def predict(self, time: float) -> float:
        if time.is_integer():
            return self.traffic[int(time)].avg
        prv_int, nxt_int = floor(time), ceil(time)
        if 0 < time < 1:
            prv, nxt = self.traffic[12], self.traffic[1]
        elif 23 < time < 24:
            prv, nxt = self.traffic[23], self.traffic[0]
        else:
            prv, nxt = self.traffic[prv_int], self.traffic[nxt_int]
        return prv.avg * (nxt_int - time) / 1.0 + nxt.avg * (time - prv_int) / 1.0

def init_traffic_model(file: TextIO) -> TrafficModel:
    traffic_model = TrafficModel()
    for line in file:
        time = int(line[line.find(' ') + 1:line.find(':')])
        traffic = float(line[line.rfind(' ') + 1:])
        traffic_model.add_measure(time, traffic)
    return traffic_model

@click.command()
@click.argument('filename', type=click.Path(exists=True, file_okay=True), default='traffic.txt')
@click.option('--debug', is_flag=True)
def analyze_traffic(filename: str, debug: bool):
    with open(filename, 'r', encoding='utf-8') as f:
        model = init_traffic_model(f)
    print('Вводите данные в формате "10.01.2021 18:15 Cisco 5300, port1  708.117", или пустую строку для выхода:')
    while True:
        line = input()
        if line == '':
            print('Выход из программы')
            break
        try:
            time = int(line[line.find(' ') + 1:line.find(':')]) + int(line[line.find(':') + 1:line.find(' ', line.find(':'))]) / 60
            traffic = float(line[line.rfind(' ') + 1:])
        except Exception:
            print('Не удалось ввести данные, попробуйте снова')
            continue
        traffic_predicted = model.predict(time)
        if debug:
            print(f'Предполагаемый - {traffic_predicted:.2f}')
        if traffic < traffic_predicted * 0.9:
            print('Трафик ниже нормы')
        elif traffic > traffic_predicted * 1.3:
            print('Трафик выше нормы')
        else:
            print('Трафик в норме')

if __name__ == '__main__':
    analyze_traffic()