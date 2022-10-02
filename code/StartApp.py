import sys
from turtle import settiltangle
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QMessageBox, \
    QTableWidgetItem, QListWidgetItem
from form1 import FigureCanvas
from main import Ui_MainWindow
from math import ceil
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as navigator
from mpl_toolkits.basemap import Basemap as Basemap
from PyQt5.QtCore import QRegExp
from PyQt5.QtGui import QRegExpValidator
from PyQt5.QtGui import QColor

class Example(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        QtWidgets.QGroupBox.__init__(self)
        self.setupUi(self)
        self.read_city_info()
        self.read_edges()
        self.load_json()
        self.comboBox_3.clear()
        self.comboBox_4.clear()
        self.comboBox_3.addItems(self.names.keys())
        self.comboBox_4.addItems(self.names.keys())
        self.comboBox_3.currentIndexChanged.connect(lambda x: self.load_names(3))
        self.comboBox_4.currentIndexChanged.connect(lambda x: self.load_names(4))
        reg_ex = QRegExp("[0-9]+].?[0-9]*")
        self.draw_map()
        self.fig = plt.figure(1)
        self.can = FigureCanvas(self.fig)
        self.horizontalLayout.addWidget(self.can)
        self.verticalLayout_2.addWidget(self.can)
        self.navcan = navigator(self.can, self)
        self.verticalLayout_2.addWidget(self.navcan)
        self.pushButton.clicked.connect(self.build_road)
        self.pushButton_2.clicked.connect(self.return_graph)
        # self.comboBox_2.clear()
        # self.comboBox_2.addItems(self.config["МТС"]['cost'].keys())
        self.operators = ["Ростелеком", "МТС", "Мегафон", "Вымпелком"]
        self.tableWidget.verticalHeader().hide()
        self.load_tables()
        self.name = 'Программа'
        self.pushButton_7.clicked.connect(self.load_tables)
        self.pushButton_3.clicked.connect(self.save_table_operators)
        self.pushButton_4.clicked.connect(self.save_table_service)
        self.pushButton_6.clicked.connect(self.add_road)
        self.pushButton_5.clicked.connect(self.del_road)
        self.road = {}
        self.road['edges'] = []
        self.road['nodes'] = []


    def del_road(self):
        for row in self.listWidget.selectedItems():
            self.road['edges'].remove(row.text().split(' - '))
        nodes = set()
        for edge in self.road['edges']:
            nodes.add(edge[0])
            nodes.add(edge[1])
        self.road['nodes'] = list(nodes)
        self.road['nodes'].sort()
        self.road['pos'] = {node: self.pos[node] for node in self.road['nodes']}

        self.show_list()
        self.draw_map_cur()
        self.get_length()

    def add_road(self):
        a = self.comboBox_3.currentText()
        b = self.comboBox_4.currentText()
        if self.names.get(a) == None or self.names.get(b) == None:
            QMessageBox.about(self, "", "Выберите города из списка")
            return
        a = self.names[a][0]
        b = self.names[b][0]
        if a > b:
            a, b = b, a
        if self.roads.get(a) == None:
            QMessageBox.about(self, "", "Телекоммуникационной сети между городами не существует")
            return
        if self.roads[a].get(b) == None:
            QMessageBox.about(self, "", "Телекоммуникационной сети между городами не существует")
            return
        path = self.roads[a][b][0]
        count_nodes = len(path) - 2
        title = ''
        for p in path:
            title += '{} - '.format(self.inds[p])
        nodes = [self.inds[self.names[self.inds[path[i]]][0]] for i in range(len(path))]
        edges = [sorted([self.inds[path[i]], self.inds[path[i + 1]]]) for i in range(len(path) - 1)]
        for node in nodes:
            if node not in self.road['nodes']:
                self.road['nodes'].append(node)
        self.road['nodes'].sort()
        for edge in edges:
            if edge not in self.road['edges']:
                self.road['edges'].append(edge)
        self.road['edges'].sort()
        self.road['pos'] = {node: self.pos[node] for node in self.road['nodes']}
        self.show_list()
        self.get_length()
        self.draw_map_cur()

    def show_list(self):
        self.listWidget.clear()
        for edge in self.road['edges']:
            self.listWidget.addItem(
                QListWidgetItem("{0} - {1}".format(edge[0], edge[1]))
            )

    def load_tables(self):
        for col, operator in enumerate(['Ростелеком','МТС', 'Мегафон', 'Вымпелком']):
            if operator not in self.config:
                continue
            for row, param in enumerate(['t','dt','k']):
                if param not in self.config[operator]:
                    continue
                self.tableWidget_2.setItem(
                    row,
                    col,
                    QTableWidgetItem(
                        str(self.config[operator][param][0]) +
                        '+' + str(self.config[operator][param][1])))
            if 'cost' not in self.config[operator]:
                continue
            s = ''
            for key in self.config[operator]['cost'].keys():
                s += str(self.config[operator]['cost'][key]) + ', '
            s = s[:-2]
            self.tableWidget_2.setItem(3, col, QTableWidgetItem(s))

        for col, operator in enumerate(['IP-телефония', 'ВКС', 'Электронная почта','Передача данных']):
            if operator not in self.config:
                continue
            for row, param in enumerate(['t','dt','k']):
                if param not in self.config[operator]:
                    continue
                self.tableWidget_3.setItem(
                    row,
                    col,
                    QTableWidgetItem(str(self.config[operator][param])))

    def save_table_operators(self):
        last = self.config
        try:
            for col, operator in enumerate(['Ростелеком', 'МТС', 'Мегафон', 'Вымпелком']):
                if operator not in self.config:
                    continue
                for row, param in enumerate(['t', 'dt', 'k']):
                    if param not in self.config[operator]:
                        continue
                    text = self.tableWidget_2.item(row, col).text().replace(' ','')
                    mas = list(map(float, text.split('+')))
                    self.config[operator][param] = mas

                if 'cost' not in self.config[operator]:
                    continue
                s = ''
                # for key in self.config[operator]['cost'].keys():
                #     s += str(self.config[operator]['cost'][key]) + ', '
                # s = s[:-2]
                mas = list(map(float, self.tableWidget_2.item(3, col).text().replace(' ','').split(',')))
                self.config[operator]['cost'] = {
                    cost:mas[i] for i, cost in enumerate(self.config[operator]['cost'].keys())
                }
                QMessageBox.about(self, self.name, "Сохранено.")
        except :
            QMessageBox.about(self, self.name, "Ошибка в данных.")
            self.config = last
            if QMessageBox.question(self, self.name,'Загрузить старые данные в таблицу?') == QMessageBox.Yes:
                self.load_tables()

    def save_table_service(self):
        last = self.config
        try:
            for col, service in enumerate(['IP-телефония', 'ВКС', 'Электронная почта', 'Передача данных']):
                if service not in self.config:
                    continue
                for row, param in enumerate(['t', 'dt', 'k']):
                    if param not in self.config[service]:
                        continue
                    self.config[service][param] = float(self.tableWidget_3.item(row, col).text().replace(' ', ''))
            QMessageBox.about(self, self.name, "Сохранено.")
        except :
            QMessageBox.about(self, self.name, "Ошибка в данных.")
            self.config = last
            if QMessageBox.question(self, self.name, 'Загрузить старые данные в таблицу?') == QMessageBox.Yes:
                self.load_tables()

    def return_graph(self):
        self.road['nodes'] = []
        self.road['edges'] = []
        self.show_list()
        self.get_length()
        plt.clf()
        m = Basemap(
            width=12000000, height=9000000,
            resolution='l', area_thresh=1000., projection='lcc',
            lat_0=61., lat_1=31., lat_2=23, lon_0=74., lon_1=54.)
        nx.draw_networkx_nodes(G=self.graph, pos=self.pos, nodelist=self.graph.nodes(), node_color='red', node_size=3)
        nx.draw_networkx_edges(G=self.graph, pos=self.pos, width=0.3, edgelist=self.graph.edges(), edge_color='blue', arrows=False)
        m.drawcountries(linewidth=1)
        m.drawcoastlines(linewidth=1)
        for col in range(1,self.tableWidget.columnCount()):
            for row in range(self.tableWidget.rowCount()):
                self.tableWidget.setItem(row, col, QTableWidgetItem())
                self.tableWidget.item(row, col).setBackground(QColor(0xffffff))

    def load_json(self):
        import json
        with open("resources/config.json", "r") as file:
            newDict = json.load(file)
            setattr(self, "config", newDict)

    def load_names(self, n):
        if n == 3:
            city = self.comboBox_3.currentText()
            self.comboBox_4.clear()
            if city not in self.names:
                self.comboBox_4.addItems(self.names.keys())
            else:
                name = self.names[city][0]
                if self.roads.get(name) == None:
                    return
                items = [self.inds[key] for key in self.roads[name].keys()]
                self.comboBox_4.addItems(items)


    def get_length(self):
        length = float(0)
        for edge in self.road['edges']:
            ind1 = self.names[edge[0]][0]
            ind2 = self.names[edge[1]][0]
            length += self.roads[ind1][ind2][1]
        self.label_2.setText('Суммарное расстояние: {} км'.format(ceil(length)))
        return length

    def draw_map_cur(self):
        G = nx.Graph()
        G.add_nodes_from(self.road['nodes'])
        G.add_edges_from(self.road['edges'])
        plt.clf()
        # return
        m = Basemap(
            width=12000000, height=9000000,
            resolution='l', area_thresh=1000., projection='lcc',
            lat_0=61., lat_1=31., lat_2=23, lon_0=74., lon_1=54.)
        nx.draw_networkx_nodes(G=G, pos=self.road['pos'], node_size=5, node_color="green")
        nx.draw_networkx_labels(G=G, pos=self.road['pos'], labels={name: name for name in self.road['nodes']},
            font_color="green", font_weight="bold")
        nx.draw_networkx_edges(G=G, pos=self.road['pos'], width=1, edgelist=self.road['edges'], edge_color="#ffa000", arrows=False)
        m.drawcountries(linewidth=1)
        m.drawcoastlines(linewidth=1)

    def draw_map(self):
        m = Basemap(
            width=12000000, height=9000000,
            resolution='l', area_thresh=1000., projection='lcc',
            lat_0=61., lat_1=31., lat_2=23, lon_0=74., lon_1=54.)
        for city in self.pos.keys():
            x, y = m(self.pos[city][1],self.pos[city][0])
            self.pos[city] = [x,y]

        self.graph = nx.MultiGraph()
        self.graph.add_nodes_from(self.names.keys(), size=3, color="red")
        self.graph.add_edges_from(self.edges)
        nx.draw_networkx_nodes(G=self.graph, pos=self.pos, nodelist=self.graph.nodes(), node_color='red', node_size=3)
        nx.draw_networkx_edges(G=self.graph, pos=self.pos,width=[0.3]*len(self.edges), edgelist=self.edges, edge_color='blue', arrows=False)
        m.drawcountries(linewidth=1)
        m.drawcoastlines(linewidth=1)
        plt.tight_layout()

    def build_road(self):
        if self.road["nodes"] == []:
            self.return_graph()
        #требования
        service = self.comboBox.currentText()
        if service not in self.config:
            QMessageBox.about(self, self.name, "Не найдены параметры данного вида услуги.")
        t = self.config[service]['t']
        dt = self.config[service]['dt']
        k = self.config[service]['k']
        c = '20'
        self.draw_map_cur()
        #исходный вид таблицы
        for col in range(1,self.tableWidget.columnCount()):
            for row in range(self.tableWidget.rowCount()):
                self.tableWidget.setItem(row, col, QTableWidgetItem(""))
                self.tableWidget.item(row, col).setBackground(QColor(0xffffff))

        #count_nodes, t, dt, c, k, service
        results = []
        count_nodes = len(self.road['nodes']) - 2
        length = self.get_length()
        road = ceil(length)
        for i, operator in enumerate(self.operators):
            params = self.config[operator]
            serv = self.config[service]
            if serv.get('t') != None:
                op = params['t'][0] + params['t'][1] * count_nodes
                if op > t:
                    self.tableWidget.item(i, 0).setBackground(QColor(255, 128, 128))
                    self.tableWidget.item(i, 1).setBackground(QColor(255, 128, 128))
                    self.tableWidget.item(i, 1).setText("Услуги оператора не соответствуют требованиям")
                    continue
            if serv.get('dt') != None:
                op = params['dt'][0] + params['dt'][1] * count_nodes
                if op > dt:
                    self.tableWidget.item(i, 0).setBackground(QColor(255, 128, 128))
                    self.tableWidget.item(i, 1).setBackground(QColor(255, 128, 128))
                    self.tableWidget.item(i, 1).setText("Услуги оператора не соответствуют требованиям")
                    continue
            if serv.get('k') != None:
                op = params['k'][0] + params['k'][1] * count_nodes
                if op > k:
                    self.tableWidget.item(i, 0).setBackground(QColor(255, 128, 128))
                    self.tableWidget.item(i, 1).setBackground(QColor(255, 128, 128))
                    self.tableWidget.item(i, 1).setText("Услуги оператора не соответствуют требованиям")
                    continue
            self.tableWidget.item(i, 1).setText(str(road * params['cost'][c]) + " руб.")
            results.append([i, road * params['cost'][c]])
            self.tableWidget.item(i, 0).setBackground(QColor(0xffa000))
            self.tableWidget.item(i, 1).setBackground(QColor(0xffa000))
        results = sorted(results,key=lambda x: x[1])
        if len(results) > 0:
            self.tableWidget.item(results[0][0], 0).setBackground(QColor(128, 255, 128))
            self.tableWidget.item(results[0][0], 1).setBackground(QColor(128, 255, 128))
        self.tableWidget.resizeColumnsToContents()


    def read_city_info(self):
        with open("resources/cities.txt", "rb") as file:
            cities = {}
            indexs = {}
            i = 0
            for line in file.read().decode("utf-8").split("\r\n"):
                mas = line.split()
                sstr = mas[0].replace("_", " ")
                cities[sstr] = [i, float(mas[1]), float(mas[2])]
                indexs[i] = sstr
                i += 1
            setattr(self, 'names', cities)
            setattr(self, 'inds', indexs)
        pos = {city: self.names[city][1:] for city in self.names.keys()}
        setattr(self, "pos", pos)


    def read_edges(self):
        edges = []
        graph = {}
        with open("resources/dj.txt") as file:
            roads = list(file.readlines())
        for i in range(len(roads)):
            road = roads[i].split()
            path = list(map(int, road[:-1]))
            length = float(road[-1])
            if len(path) == 2:
                edges.append([self.inds[path[0]], self.inds[path[1]], length])
            a = path[0]
            b = path[-1]
            if graph.get(a) == None:
                graph[a] = dict()
            if graph[a].get(b) == None:
                graph[a][b] = [path, length]
        setattr(self, "edges", edges)
        setattr(self, "roads", graph)





if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = Example()
    window.show()
    sys.exit(app.exec_())
