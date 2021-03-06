
PLD_HEADER_TEMPLATE_FILE = '''Generated by the System                                          06-JAN-80 00:00
--------------------------------------------------------------------------------
LOCAL GEODETIC DATUM: {DATUM:<6s}

NUM  STATION NAME           VX (M/Y)       VY (M/Y)       VZ (M/Y)  FLAG   PLATE

'''

PLD_BODY_TEMPLATE_FILE = '{ID:>3d}  {MARKER NAME:<4s} {MARKER NUMBER:<9s}                                                        {PLATE:<4s}\n'


CRD_HEADER_TEMPLATE_FILE = '''Generated by the System                                          06-JAN-80 00:00
--------------------------------------------------------------------------------
LOCAL GEODETIC DATUM: {DATUM:<8s}          EPOCH: {EPOCH}

NUM  STATION NAME           X (M)          Y (M)          Z (M)     FLAG

'''

CRD_BODY_TEMPLATE_FILE = '{ID:>3d}  {MARKER NAME:<4s} {MARKER NUMBER:<9s}   {APPROX POSITION XYZ[0]:>14.5f} {APPROX POSITION XYZ[1]:>14.5f} {APPROX POSITION XYZ[2]:>14.5f}    {FLAG}\n'


ABB_HEADER_TEMPLATE_FILE = '''Generated by the System                                          06-JAN-80 00:00
--------------------------------------------------------------------------------

Station name             4-ID    2-ID    Remark
****************         ****     **     ***************************************
'''

ABB_BODY_TEMPLATE_FILE = '{MARKER NAME:<4s} {MARKER NUMBER:<9s}           {MARKER NAME:<4s}     {ID2:<2s}\n'

STA_HEADER_T1_TEMPLATE_FILE = '''Generated by the System                                          06-JAN-80 00:00
--------------------------------------------------------------------------------

FORMAT VERSION: 1.01
TECHNIQUE:      GNSS

TYPE 001: RENAMING OF STATIONS
------------------------------

STATION NAME          FLG          FROM                   TO         OLD STATION NAME      REMARK
****************      ***  YYYY MM DD HH MM SS  YYYY MM DD HH MM SS  ********************  ************************
'''

STA_BODY1_TEMPLATE_FILE = '{MARKER NAME:<4s} {MARKER NUMBER:<9s}        001                                            {MARKER NAME:<4s}*\n'

STA_HEADER_T2_TEMPLATE_FILE = '''

TYPE 002: STATION INFORMATION
-----------------------------

STATION NAME          FLG          FROM                   TO         RECEIVER TYPE         RECEIVER SERIAL NBR   REC #   ANTENNA TYPE          ANTENNA SERIAL NBR    ANT #    NORTH      EAST      UP      DESCRIPTION             REMARK
****************      ***  YYYY MM DD HH MM SS  YYYY MM DD HH MM SS  ********************  ********************  ******  ********************  ********************  ******  ***.****  ***.****  ***.****  **********************  ************************
'''
STA_BODY2_TEMPLATE_FILE = '{MARKER NAME:<4s} {MARKER NUMBER:<9s}        001                                            {REC # / TYPE / VERS[1]:<20s}                        999999  {ANT # / TYPE[1]:<20s}                        999999  {ANTENNA DELTA H/E/N[2]:>8.4f}  {ANTENNA DELTA H/E/N[1]:>8.4f}  {ANTENNA DELTA H/E/N[0]:>8.4f}  None\n'

STA_FOOTER_TEMPLATE_FILE = '''

TYPE 003: HANDLING OF STATION PROBLEMS
--------------------------------------

STATION NAME          FLG          FROM                   TO         REMARK
****************      ***  YYYY MM DD HH MM SS  YYYY MM DD HH MM SS  ************************************************************


TYPE 004: STATION COORDINATES AND VELOCITIES (ADDNEQ)
-----------------------------------------------------
                                            RELATIVE CONSTR. POSITION     RELATIVE CONSTR. VELOCITY
STATION NAME 1        STATION NAME 2        NORTH     EAST      UP        NORTH     EAST      UP
****************      ****************      **.*****  **.*****  **.*****  **.*****  **.*****  **.*****


TYPE 005: HANDLING STATION TYPES
--------------------------------

STATION NAME          FLG  FROM                 TO                   MARKER TYPE           REMARK
****************      ***  YYYY MM DD HH MM SS  YYYY MM DD HH MM SS  ********************  ************************




'''

SES_TEMPLATE_FILE = '''
LIST_OF_SESSIONS 1  "???0" "" "00 00 00" "" "23 59 59"
  ## widget = uniline; check_strlen.1 = 4; numlines = 24
  ## check_type.3 = time; check_type.5 = time

MSG_LIST_OF_SESSIONS 1  "List of sessions"


# BEGIN_PANEL NO_CONDITION #####################################################
# SESSION TABLE                                                                #
#                                                                              #
#                START EPOCH         END EPOCH                                 #
#    > ID__ yyyy_mm_dd hh_mm_ss yyyy_mm_dd hh_mm_ss     <                      # LIST_OF_SESSIONS
#                                                                              #
# END_PANEL ####################################################################

'''
