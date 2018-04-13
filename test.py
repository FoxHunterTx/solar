

def get_current_ac(data=None):
  if data['Volt'] is not "0" and data['Watt'] is not "0":
    tmp1 = str(data['Watt'])
    if tmp1 != "" and tmp1 != "0":
      print "in get_ if"
      return (float(data['Watt'])/float(data['Volt']))
    else:
      print "in get_ else"
      return (float(0.00))


print "test"

testdic ={'Watt':"",'Volt':"4"}
tmp1 = get_current_ac(testdic)
print tmp1


