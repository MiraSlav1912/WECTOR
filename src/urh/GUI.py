import matplotlib.pyplot as plt
import pylab
import zmq
import time


def rng(start,end,div):
    return range(int(start),int(end),int((end - start)/div))

def GUI():
    frequency = rng(500e6, 1500e6, 50)
    
    context = zmq.Context()
    results_receiver = context.socket(zmq.PULL)
    results_receiver.bind("tcp://127.0.0.1:5558")
    a  = results_receiver.recv_json()

    while True:
        TIME = time.time()
        SUM = results_receiver.recv_json()
        #SUM = results_receiver.recv_json()
        #print(SUM)
        color = '#08F208'
        plt.clf()
        y_pos = range(len(frequency))
        rects = pylab.bar(y_pos, SUM, color=[color], edgecolor=['red'])
        f_to_str = [' ' for i in range(len(frequency))]
        for i in range(len(SUM)):
            if (SUM[i] > (sum(SUM) / len(SUM)) * 1.5):
                ff = (frequency[1] - frequency[0]) / 2
                f_to_str[i] = str(frequency[i])[:4]
        top = 200
        if max(SUM) > top:
            top = max(SUM) + 100
        plt.ylim(10, top)
        plt.xticks(y_pos, f_to_str, rotation='vertical')

        drs = []
        for rect in rects:
            dr = DraggableRectangle(rect, frequency, SUM)
            dr.connect()
            drs.append(dr)

        pylab.draw()
        plt.pause(0.001)
        print('-' * 50)
        print('draw: ', time.time() - TIME)
        print('-' * 50)
        print('\n' * 10)
        # print('-' * 50)

class DraggableRectangle:
    def __init__(self, rect,frequency,SUM):
        self.frequency = frequency
        self.SUM = SUM
        self.rect = rect
        #self.press = None

    def connect(self):
        'connect to all the events we need'
        self.cidpress = self.rect.figure.canvas.mpl_connect(
            'button_press_event', self.on_press)


    def on_press(self, event):
        pass
        'on button press we will see if the mouse is over us and store some data'
        if event.inaxes != self.rect.axes: return

        contains, attrd = self.rect.contains(event)
        if not contains: return
        print('|'*50)
        print(self.frequency[int(self.rect.xy[0]+0.4)], ' Gh', self.SUM[int(self.rect.xy[0]+0.4)], ' Ed')
        print('|' * 50)
        time.sleep(1)


    def on_release(self, event):
        'on release we reset the press data'
        self.press = None
        #self.rect.figure.canvas.draw()

    def disconnect(self):
        'disconnect all the stored connection ids'
        self.rect.figure.canvas.mpl_disconnect(self.cidpress)
        self.rect.figure.canvas.mpl_disconnect(self.cidrelease)
        self.rect.figure.canvas.mpl_disconnect(self.cidmotion)

GUI()