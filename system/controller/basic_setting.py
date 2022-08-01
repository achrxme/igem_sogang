from i611_MCS import *
from i611_extend import *
from i611_io import *
from teachdata import *
from rbsys import *
from i611_common import *
from i611shm import *

def main():

    rb = i611Robot()
    _BASE = Base()
    rb.open()
    IOinit(rb)

    m_basic = MotionParam( lin_speed = 60, jnt_speed = 20 )
    rb.motionparam(m_basic)

    
    rb.close()
    

if __name__ == '__main__':
        main()
