#!/usr/bin/python
#-*- coding: iso-8859-15 -*-
# INDUINO METEOSTATION
# http://induino.wordpress.com 
# 
# NACHO MAS 2013

import sys, os
import rrdtool
import time
from meteoconfig import *
import math
from time import gmtime

from indiclient import *
import signal
import simplejson
import gc
#from guppy import hpy

signal.signal(signal.SIGINT, signal.SIG_DFL)

blue="0080F0"
orange="F08000"
red="FA2000"
white="AAAAAA"

P0=math.floor(1013.25/math.exp(ALTITUDE/8000.))
Pdelta=25
Pmin=P0-Pdelta
Pmax=P0+Pdelta

preamble=["--width","600",
         "--height","300",
         "--color", "FONT#FF0000",
	 "--color", "SHADEA#00000000",
	 "--color", "SHADEB#00000000",
	 "--color", "BACK#00000000",
         "--color", "CANVAS#00000000"]

def graphs(time):
	ret = rrdtool.graph( CHARTPATH+"temp"+str(time)+".png","--start","-"+str(time)+"h","-E",
          preamble,
	 "--title","Temperature and Dew Point",
	 "--vertical-label=Celsius C",
	 "DEF:T="+RRDFILE+":T:AVERAGE",
	 "DEF:Dew="+RRDFILE+":Dew:AVERAGE",
         "COMMENT:\\t\\t\\tCurrent\:\\t  Min\:\\t\\t  Max\:\\n",
         "LINE1:T#"+red+":Ambient Temperature",
         "GPRINT:T:LAST:    %3.2lf",
         "GPRINT:T:MIN:\\t%3.2lf",
         "GPRINT:T:MAX:\\t  %3.2lf\\n",
	 "AREA:Dew#"+red+"40:Dew Point",
         "GPRINT:Dew:LAST:\\t      %3.2lf",
         "GPRINT:Dew:MIN:\\t%3.2lf",
         "GPRINT:Dew:MAX:\\t  %3.2lf\\n",
	 "HRULE:0#00FFFFAA:ZERO\\n"
        )

	ret = rrdtool.graph( CHARTPATH+"pressure"+str(time)+".png","-A","--start","-"+str(time)+"h","-E",
          preamble,
	 "--title","Air Pressure",
	 "--vertical-label=mBar",
	 "-u",str(Pmax),
	 "-l",str(Pmin),
	 "-r",
	 "DEF:P="+RRDFILE+":P:AVERAGE",
         "COMMENT:\\t\\t\\tCurrent\:\\t  Min\:\\t\\t  Max\:\\n",
	 "LINE1:P#"+blue+":Air Pressure",
         "GPRINT:P:LAST:\\t %3.2lf",
         "GPRINT:P:MIN:      %3.2lf",
         "GPRINT:P:MAX:\\t%3.2lf\\n",
	 "HRULE:"+str(P0)+"#"+red+"AA:Standard"
        )

	ret = rrdtool.graph( CHARTPATH+"hr"+str(time)+".png","--start","-"+str(time)+"h","-E",
          preamble,
	 "-u","105",
	 "-l","-5",
	 "-r",
	 "--title","Humidity",
	 "--vertical-label=%",
	 "DEF:HR="+RRDFILE+":HR:AVERAGE",
         "COMMENT:\\t\\tCurrent\:\\t   Min\:\\t\\t   Max\:\\n",
	 "LINE1:HR#"+blue+":Humidity",
         "GPRINT:HR:LAST:      %3.2lf",
         "GPRINT:HR:MIN:\\t%3.2lf",
         "GPRINT:HR:MAX:\\t %3.2lf\\n",
	 "HRULE:100#FF00FFAA:100%\\n",
	 "HRULE:0#00FFFFAA:0%")

	ret = rrdtool.graph( CHARTPATH+"light"+str(time)+".png","--start","-"+str(time)+"h","-E",
          preamble,
	 "--title","Sky Quality (SQM)",
	 "--vertical-label=mag/arcs^2",
	 "DEF:Light="+RRDFILE+":Light:AVERAGE",
         "COMMENT:\\t\\tCurrent\:\\t   Min\:\\t\\t    Max\:\\n",
         "LINE1:Light#"+blue+":SQM",
         "GPRINT:Light:LAST:\\t    %3.2lf",
         "GPRINT:Light:MIN:\\t%3.2lf",
         "GPRINT:Light:MAX:\\t %3.2lf\\n")

	ret = rrdtool.graph( CHARTPATH+"clouds"+str(time)+".png","-A","--start","-"+str(time)+"h","-E",
          preamble,
	 "--title","Clouds",
	 "--vertical-label=%",
	 "-u","102",
	 "-l","-2",
	 "-r",
	 "DEF:clouds="+RRDFILE+":clouds:AVERAGE",
	 "DEF:cloudFlag="+RRDFILE+":cloudFlag:AVERAGE",
	 "CDEF:cloudy=clouds,cloudFlag,*",
         "COMMENT:\\t\\tCurrent\:\\t   Min\:\\t\\t    Max\:\\n",
	 "LINE1:clouds#"+orange+":clouds",
         "GPRINT:clouds:LAST:\\t%3.2lf",
         "GPRINT:clouds:MIN:\\t%3.2lf",
         "GPRINT:clouds:MAX:\\t %3.2lf\\n",
	 "AREA:cloudy#FFFFFF40:CloudyFlag\\n",
	 "AREA:30#00000a40:Clear\\n",
	 "AREA:40#0000AA40:Cloudy\\n:STACK",
	 "AREA:32#0000FF40:Overcast:STACK")

	ret = rrdtool.graph( CHARTPATH+"skyT"+str(time)+".png","--start","-"+str(time)+"h","-E",
          preamble,
	 "--title","Sky Temperatures",
	 "--vertical-label=Celsius C",
	 "DEF:skyT="+RRDFILE+":skyT:AVERAGE",
	 "DEF:IR="+RRDFILE+":IR:AVERAGE",
	 "DEF:Thr="+RRDFILE+":Thr:AVERAGE",
	 "CDEF:Tc=IR,skyT,-",
         "COMMENT:\\t\\t\\tCurrent\:\\t   Min\:\\t\\t  Max\:\\n",
	 "LINE1:skyT#"+blue+":Corrected Sky T",
         "GPRINT:skyT:LAST:\\t%3.2lf",
         "GPRINT:skyT:MIN:\\t%3.2lf",
         "GPRINT:skyT:MAX:\\t %3.2lf\\n",
	 "LINE1:IR#"+orange+":Actual Sky T",
         "GPRINT:IR:LAST:\\t   %3.2lf",
         "GPRINT:IR:MIN:\\t %3.2lf",
         "GPRINT:IR:MAX:\\t %3.2lf\\n",
	 "LINE1:Thr#"+red+":Ambient T",
         "GPRINT:Thr:LAST:\\t      %3.2lf",
         "GPRINT:Thr:MIN:\\t %3.2lf",
         "GPRINT:Thr:MAX:\\t %3.2lf\\n",
	 "LINE1:Tc#"+white+":Correction",
         "GPRINT:Tc:LAST:\\t     %3.2lf",
         "GPRINT:Tc:MIN:\\t %3.2lf",
         "GPRINT:Tc:MAX:\\t %3.2lf\\n",
	 "HRULE:0#00FFFFAA:ZERO")


def recv_indi(indi):
	tim=time.localtime()
        vectorHR=indi.get_vector(INDIDEVICE,SENSOR_HUMIDITY)
	HR=vectorHR.get_element(SENSOR_HUMIDITY_HUM).get_float()
        Thr=vectorHR.get_element(SENSOR_HUMIDITY_TEMP).get_float()

        vectorPressure=indi.get_vector(INDIDEVICE, SENSOR_PRESSURE)
	P=vectorPressure.get_element(SENSOR_PRESSURE_PRES).get_float()
        Tp=vectorPressure.get_element(SENSOR_PRESSURE_TEMP).get_float()

        vectorIR=indi.get_vector(INDIDEVICE, SENSOR_IR)
	IR=vectorIR.get_element(SENSOR_IR_IR).get_float()
	Tir=vectorIR.get_element(SENSOR_IR_TEMP).get_float()

        vectorMeteo=indi.get_vector(INDIDEVICE, WEATHER)
	dew=vectorMeteo.get_element(WEATHER_DEWPOINT).get_float()
	clouds=vectorMeteo.get_element(WEATHER_CLOUDS).get_float()
	T=vectorMeteo.get_element(WEATHER_TEMP).get_float()
        skyT=vectorMeteo.get_element(WEATHER_SKY_TEMP).get_float()

        vectorSQM=indi.get_vector(INDIDEVICE, WEATHER_SQM)
	sqm=vectorSQM.get_element(WEATHER_SQM_SQM).get_float()
   
        statusVector=indi.get_vector(INDIDEVICE, WEATHER_STATUS)
        cloudFlag=int(not (statusVector.get_element(WEATHER_STATUS_CLOUDS).is_ok() or
                           statusVector.get_element(WEATHER_STATUS_CLOUDS).is_idle()))
        dewFlag=int(not (statusVector.get_element(WEATHER_STATUS_DEW).is_ok() or
                         statusVector.get_element(WEATHER_STATUS_DEW).is_idle()))
        frezzingFlag=int(not (statusVector.get_element(WEATHER_STATUS_TEMP).is_ok() or
                              statusVector.get_element(WEATHER_STATUS_TEMP).is_idle()))
  
        return (("HR",HR),("Thr",Thr),("IR",IR),("Tir",Tir),("P",P),("Tp",Tp),("Dew",dew),("SQM",sqm),
           ("T",T),("clouds",clouds),("skyT",skyT),("cloudFlag",cloudFlag),("dewFlag",dewFlag),
           ("frezzingFlag",frezzingFlag))


def connect(indi):
    #connect ones to configure the port
    connection = indi.get_vector(INDIDEVICE, "CONNECTION")
    if connection.get_element("CONNECT").get_active() == False:
        # set the configured port
        indi.set_and_send_text(INDIDEVICE,"DEVICE_PORT","PORT",INDIDEVICEPORT)

        # connect driver
        connection.set_by_elementname("CONNECT")
        indi.send_vector(connection)
        print "CONNECT INDI Server host:%s port:%s device:%s" % (INDISERVER,INDIPORT,INDIDEVICE)
        time.sleep(5)

def init():
        ## Write configuration javascript
        fi=open(CHARTPATH+"meteoconfig.js","w")
        fi.write("var altitude=%s\n" % ALTITUDE)
        fi.write("var sitename=\"%s\"\n" % SITENAME)
        fi.write("var INDISERVER=\"%s\"\n" % INDISERVER)
        fi.write("var INDIPORT=%s\n" % INDIPORT)
        fi.write("var INDIDEVICE=\"%s\"\n" % INDIDEVICE)
        fi.write("var INDIDEVICEPORT=\"%s\"\n" % INDIDEVICEPORT)
        fi.write("var OWNERNAME=\"%s\"\n" % OWNERNAME)
        fi.close()
