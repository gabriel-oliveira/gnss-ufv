
PLD_TEMPLATE_FILE = '''Example plate assignement                                        14-SEP-11 21:46
--------------------------------------------------------------------------------
LOCAL GEODETIC DATUM: IGS14

NUM  STATION NAME           VX (M/Y)       VY (M/Y)       VZ (M/Y)  FLAG   PLATE

  1  {MARKER NAME:<4s} {MARKER NUMBER:<9s}                                                        SOAM

'''

CRD_TEMPLATE_FILE = ''

STA_TEMPLATE_FILE = '''EXAMPLE STATION INFORMATION FILE                                 14-JAN-13 14:21
--------------------------------------------------------------------------------

FORMAT VERSION: 1.01
TECHNIQUE:      GNSS

TYPE 001: RENAMING OF STATIONS
------------------------------

STATION NAME          FLG          FROM                   TO         OLD STATION NAME      REMARK
****************      ***  YYYY MM DD HH MM SS  YYYY MM DD HH MM SS  ********************  ************************
{MARKER NAME:<4s} {MARKER NUMBER:<9s}        001                                            {MARKER NAME:<4s}*


TYPE 002: STATION INFORMATION
-----------------------------

STATION NAME          FLG          FROM                   TO         RECEIVER TYPE         RECEIVER SERIAL NBR   REC #   ANTENNA TYPE          ANTENNA SERIAL NBR    ANT #    NORTH      EAST      UP      DESCRIPTION             REMARK
****************      ***  YYYY MM DD HH MM SS  YYYY MM DD HH MM SS  ********************  ********************  ******  ********************  ********************  ******  ***.****  ***.****  ***.****  **********************  ************************
{MARKER NAME:<4s} {MARKER NUMBER:<9s}        001                                            {REC # / TYPE / VERS[1]:<20s}                        999999  {ANT # / TYPE[1]:<20s}                        999999  {ANTENNA DELTA H/E/N[2]:>8.4f}  {ANTENNA DELTA H/E/N[1]:>8.4f}  {ANTENNA DELTA H/E/N[0]:>8.4f}  None


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
