import threading
import os
import json
from urllib.parse import urlencode
from urllib.request import urlopen
from IPython.display import display
import ipywidgets as widgets
from qiskit import IBMQ, execute, QuantumCircuit, QuantumRegister, ClassicalRegister, BasicAer
from qiskit.tools.monitor import job_monitor

script_dir = os.path.dirname(__file__)

MY_PROVIDER = IBMQ.load_account()


__all__ = ['quantum_slot_machine']

def quantum_slot_machine():
    """A slot machine that uses random numbers generated
    by quantum mechanical processses.
    """
    qslot = widgets.VBox(children=[slot, opts])
    qslot.children[0].children[1].children[7].children[1]._qslot = qslot
    qslot.children[0].children[1].children[7].children[1].on_click(pull_slot)
    ibmq_thread = threading.Thread(target=get_ibmq_ints, args=(qslot,))
    ibmq_thread.start()
    display(qslot)


def get_slot_values(backend, qslot):
    if backend == 'qasm_simulator':
        back = BasicAer.get_backend('qasm_simulator')
        q = QuantumRegister(9, name='q')
        c = ClassicalRegister(9, name='c')
        qc = QuantumCircuit(q, c)
        for kk in range(9):
            qc.h(q[kk])
        qc.measure(q, c)
        job = execute(qc, backend=back, shots=1)
        result = job.result()
        counts = list(result.get_counts().keys())[0]
        return int(counts[0:3], 2), int(counts[3:6], 2), int(counts[6:9], 2)
    elif backend == 'ibmqx2':
        int1 = qslot.children[0]._stored_ints.pop(0)
        int2 = qslot.children[0]._stored_ints.pop(0)
        int3 = qslot.children[0]._stored_ints.pop(0)
        if len(qslot.children[0]._stored_ints) == 0:
            ibmq_thread = threading.Thread(target=get_ibmq_ints, args=(qslot,))
            ibmq_thread.start()
        return int1, int2, int3

    elif backend == 'ANU QRNG':
        URL = 'https://qrng.anu.edu.au/API/jsonI.php'
        url = URL + '?' + urlencode({'type': 'hex16',
                                     'length': 3,
                                     'size': 1})
        data = json.loads(urlopen(url).read().decode('ascii'))
        rngs = [int(bin(int(kk, 16))[2:].zfill(8)[:3], 2)
                for kk in data['data']]
        return rngs[0], rngs[1], rngs[2]
    else:
        raise Exception('Invalid backend choice.')


def set_images(a, b, c, qslot):
    slot0 = qslot.children[0].children[1].children[1]
    slot1 = qslot.children[0].children[1].children[3]
    slot2 = qslot.children[0].children[1].children[5]
    slot0.value = qslot.children[0]._images[a]
    slot1.value = qslot.children[0]._images[b]
    slot2.value = qslot.children[0]._images[c]

def update_credits(change, qslot):
    qslot.children[0]._credits += change
    qslot.children[1].children[1].value = front_str + \
        str(qslot.children[0]._credits)+back_str

def compute_payout(ints, qslot):
    out = 1
    #Paytable
    # all sevens
    if all([x == 7 for x in ints]):
        value = 700
    # all watermelons
    elif all([x == 6 for x in ints]):
        value = 200
    # all strawberry
    elif all([x == 5 for x in ints]):
        value = 10
    # all orange
    elif all([x == 4 for x in ints]):
        value = 20
    # all lemon
    elif all([x == 3 for x in ints]):
        value = 60
    # all grape
    elif all([x == 2 for x in ints]):
        value = 15
    # all cherry
    elif all([x == 1 for x in ints]):
        value = 40
    # all bell
    elif all([x == 0 for x in ints]):
        value = 80
    # two bells
    elif sum([x == 0 for x in ints]) == 2:
        value = 5
    # two bells
    elif sum([x == 0 for x in ints]) == 1:
        value = 1
    else:
        value = 0
    if value:
        update_credits(value, qslot)

    # if no credits left
    if qslot.children[0]._credits <= 0:
        qslot.children[1].children[1].value = front_str + \
            "LOSE"+back_str
        out = 0
    return out


def pull_slot(b):
    qslot = b._qslot
    update_credits(-1, qslot)
    b.disabled = True
    set_images(-1, -1, -1, qslot)
    backend = qslot.children[1].children[0].value
    ints = get_slot_values(backend, qslot)
    set_images(ints[0], ints[1], ints[2], qslot)
    alive = compute_payout(ints, qslot)
    if alive:
        b.disabled = False

def choose_backend():
    from qiskit.providers.ibmq import least_busy
    large_enough_devices = MY_PROVIDER.backends(
        filters=lambda x: x.configuration().n_qubits >= 3
        and not x.configuration().simulator)
    return least_busy(large_enough_devices)

# generate new ibm q values
def get_ibmq_ints(qslot):
    qslot.children[1].children[0].options = ['qasm_simulator', 'ANU QRNG']
    qslot.children[1].children[0].value = 'qasm_simulator'
#    back = MY_PROVIDER.get_backend('ibmq_essex')
    back = choose_backend()
    q = QuantumRegister(3, name='q')
    c = ClassicalRegister(3, name='c')
    qc = QuantumCircuit(q, c)
    for kk in range(3):
        qc.h(q[kk])
    qc.measure(q, c)
    job = execute(qc, backend=back, shots=300, memory=True)
    qslot.children[1].children[2].clear_output()
    with qslot.children[1].children[2]:
        job_monitor(job)
    qslot.children[0]._stored_ints = [
        int(kk, 16) for kk in job.result().results[0].data.memory]

    qslot.children[1].children[0].options = ['qasm_simulator', 'ibmqx2', 'ANU QRNG']


#top
top_file = open(script_dir+"/machine/slot_top.png", "rb")
top_image = top_file.read()
slot_top = widgets.Image(
    value=top_image,
    format='png',
    width='100%',
    height='auto',
    layout=widgets.Layout(margin='0px 0px 0px 0px')
)

#bottom
bottom_file = open(script_dir+"/machine/slot_bottom.png", "rb")
bottom_image = bottom_file.read()
slot_bottom = widgets.Image(
    value=bottom_image,
    format='png',
    width='100%',
    height='auto',
    layout=widgets.Layout(margin='0px 0px 0px 0px')
)

#left
left_file = open(script_dir+"/machine/slot_left.png", "rb")
left_image = left_file.read()
left = widgets.Image(
    value=left_image,
    format='png',
    width='auto',
    height='auto',
    margin='0px 0px 0px 0px'
)


#left
right_file = open(script_dir+"/machine/slot_right.png", "rb")
right_image = right_file.read()
right = widgets.Image(
    value=right_image,
    format='png',
    width='auto',
    height='auto',
    margin='0px 0px 0px 0px'
)


#mid
mid_file = open(script_dir+"/machine/slot_middle.png", "rb")
mid_image = mid_file.read()
mid = widgets.Image(
    value=mid_image,
    format='png',
    width='auto',
    height='auto',
    margin='0px 0px 0px 0px'
)


#symbols
blank_sym = open(script_dir+"/symbols/blank.png", "rb")
blank_img = blank_sym.read()

slot0 = widgets.Image(
    value=blank_img,
    format='png',
    width='auto',
    height='auto',
    max_width='175px',
    max_height='175px'
)
slot1 = widgets.Image(
    value=blank_img,
    format='png',
    width='auto',
    height='auto',
    max_width='175px',
    max_height='175px'
)
slot2 = widgets.Image(
    value=blank_img,
    format='png',
    width='auto',
    height='auto',
    max_width='175px',
    max_height='175px'
)

#arm
arm_upper_file = open(script_dir+"/machine/slot_handle_upper.png", "rb")
arm__upper_image = arm_upper_file.read()
arm_upper = widgets.Image(
    value=arm__upper_image,
    format='png',
    width='auto')


arm_lower_file = open(script_dir+"/machine/slot_handle_lower.png", "rb")
arm__lower_image = arm_lower_file.read()
arm_lower = widgets.Image(
    value=arm__lower_image,
    format='png',
    width='auto')

arm_button = widgets.Button(description='PUSH', button_style='danger',
                            layout=widgets.Layout(width='120px', height='auto', margin='0px 35px'))
arm_button.style.font_weight = 'bold'


arm = widgets.VBox(children=[arm_upper, arm_button, arm_lower],
                   layout=widgets.Layout(width='auto',
                                         margin='0px 0px 0px 0px'))

items = [left, slot0, mid, slot1, mid, slot2, right, arm]
box_layout = widgets.Layout(display='flex',
                            flex_flow='row',
                            align_items='center',
                            width='auto',
                            margin='0px 0px 0px 0px')
slot_middle = widgets.Box(children=items, layout=box_layout)

slot = widgets.VBox(children=[slot_top, slot_middle, slot_bottom],
                    layout=widgets.Layout(display='flex',
                                          flex_flow='column',
                                          align_items='center',
                                          width='auto',
                                          margin='0px 0px 0px 0px'))

slot._stored_ints = []
imgs = ['waiting.png', 'bell.png', 'cherry.png', 'grape.png', 'lemon.png', 'orange.png',
        'strawberry.png', 'watermelon.png', 'seven.png']
slot._images = {}
for kk, img in enumerate(imgs):
    slot._images[kk-1] = open(script_dir+"/symbols/%s" % img, "rb").read()

slot._credits = 20

solver = widgets.Dropdown(
    options=['qasm_simulator', 'ibmqx2', 'ANU QRNG'],
    value='qasm_simulator',
    description='',
    disabled=False,
    layout=widgets.Layout(width='25%', padding='10px')
)

front_str = "<div style = 'background-color:#000000; height:70px; text-align:right;padding:10px' > <p style='color:#FFFFFF; font-size: 60px;margin: 10px'>"
back_str = "</p></div>"

payout = widgets.HTML(
    value=front_str+str(20)+back_str,
    placeholder='',
    description='',
    layout=widgets.Layout(width='33%', height='70px')
)

out = widgets.Output(layout=widgets.Layout(width='33%', padding='10px'))

opts = widgets.HBox(children=[solver, payout, out],
                    layout=widgets.Layout(width='100%',
                                          justify_content='center',
                                          border='2px solid black'))
