import os
from odtk import Client, ClientException, ClientExceptionCodes

# Make sure ODTK is running, with the HTTP server started (default port is 9393) before running this script


# The following initializes the client to connect to ODTK at the default port
client = Client()
odtk = client.get_root()

# Notes on accessing attributes:
# - use square brackets to access an item by index (as in: odtk.scenario[0],
#   scenario.Satellite['mySat']).
# - except for the 'Count', 'Item', and 'ItemByName' attributes, an explicit call to the 'eval()' function,
#   as in 'satellite.name.eval()', is needed to get the value associated with an ODTK attribute;
#   in the previous example, a call to 'satellite.name' will only return a proxy object
#   that represents the satellite name attribute if '.eval()' is omitted.

# Starting with the ODTK root object, each object provides access to its sub objects via the 'children' scope.
# Use 'children' to test if there are any objects and then use class name to access them.
odtk_child_count = odtk.children.count

# Creating, Deleting, Saving, and Loading Objects
# There are a number of functions in ODTK to manage the scenario and other objects.
# New objects are created with the CreateObj function. It takes three parameters: the parent object of the new object,
# the type of object to create, and the name of the new object. This function returns a handle to
# the new object. NOTE: do not give objects ODTK class names ("Scenario", "Satellite", "Filter", etc.).

# ensure new scenario
if odtk_child_count > 0:
    # close scenario
    odtk.application.deleteObject('', odtk.scenario[0])
    print('Scenario closed.')
odtk.application.createObj(odtk, 'Scenario', 'TestScenario')
print('Scenario created.')

# create satellites
zeroth_satellite_name = 'mySat'
zero_as_satellite_name = '0'
odtk.application.createObj(odtk.scenario[0], 'Satellite', zeroth_satellite_name)
my_other_sat = odtk.application.createObj(odtk.scenario[0], 'Satellite', 'myOtherSat')
odtk.application.createObj(odtk.scenario[0], 'Satellite', zero_as_satellite_name)
print('Satellites created.')

# create filter
odtk.application.createObj(odtk.scenario[0], 'Filter', 'Filter1')

# You can save the scenario or any object to a file with the SaveObj function.
# It takes three parameters: the object handle, the destination file name, and the boolean SaveObjectChildren flag.
this_dir_path = os.path.dirname(os.path.realpath(__file__))
scenario_file_path = os.path.join(this_dir_path, 'Example1.sco')
odtk.SaveObj(odtk.scenario[0], scenario_file_path, True)
print(f'Scenario saved to {scenario_file_path}')

# The DeleteObject function takes an object handle and returns a success status.
deleted = odtk.deleteobject(my_other_sat)
print(f'Deleted myOtherSat: {deleted}')

# NOTE: Only one scenario at a time is allowed; unload the current scenario before loading the next one.
# To load an object at a later time, use the LoadObject function.
# Its parameters are the path of the parent object where the new object is to be loaded and the source file name
# containing the object to be loaded.

# close the scenario
odtk.application.deleteObject('', odtk.scenario[0])
# load the scenario
scenario_loaded = odtk.LoadObject('', scenario_file_path)
print(f'Scenario loaded from {scenario_file_path}: {scenario_loaded}')

# As a side effect of supporting various languages there are multiple ways to get access to the same object.
# For instance, "mySat" could be referred to as:

scenario = odtk.scenario[0]
satellite = scenario.mySat
print(f'Satellite name using scenario.mySat: {satellite.name.eval()}')
satellite = scenario.Satellite[0]
print(f'Satellite name using scenario.Satellite[0]: {satellite.name.eval()}')
satellite = scenario.Satellite[zeroth_satellite_name]
print(f'Satellite name using scenario.Satellite[\'{zeroth_satellite_name}\']: {satellite.name.eval()}')
satellite = scenario.Children.Satellite[0]
print(f'Satellite name using scenario.Children.Satellite[0]: {satellite.name.eval()}')
satellite = scenario.Children['Satellite'][0]
print(f'Satellite name using scenario.Children[\'Satellite\'][0]: {satellite.name.eval()}')
satellite = scenario.Children['Satellite'].Item[0]
print(f'Satellite name using scenario.Children[\'Satellite\'].Item[0]: {satellite.name.eval()}')
satellite = scenario.Children['Satellite'].Item[zeroth_satellite_name]
print(f'Satellite name using scenario.Children[\'Satellite\'].Item[\'{zeroth_satellite_name}\']: '
      f'{satellite.name.eval()}')
satellite = scenario.Children['Satellite'].ItemByName[zeroth_satellite_name]
print(f'Satellite name using scenario.Children[\'Satellite\'].ItemByName[\'{zeroth_satellite_name}\']: '
      f'{satellite.name.eval()}')

# To display the names of each of the satellites in your scenario you could use the following:
print('Names of satellites in the scenario:')
for satellite in odtk.scenario[0].Children['Satellite']:
    print(f'   {satellite.name.eval()}')

# Testing To See If An Object Exists
satellites = odtk.scenario[0].Children['Satellite']
# access by index
satellite_name = satellites[0].name.eval()
print(f'satellites[0] name: {satellite_name}')
# access by name
print(f'satellites[\"' + satellite_name + '\"] name: {satellites[satellite_name].name.eval()}')
# access using a name that is numeric (string)
satellite_name = satellites[zero_as_satellite_name].name.eval()
print(f'satellites[\"{zero_as_satellite_name}\"] name: {satellite_name}')

try:
    # access by invalid index should throw an exception
    satellite_name = satellites[7].name.eval()
    raise Exception('The expected exception was not thrown.')
except ClientException as e:
    if e.error_code == ClientExceptionCodes.INVALID_ATTRIBUTE_PATH and 'Index Out of Range' in str(e):
        print('Non-existent satellite reference threw an exception as expected.')
    else:
        raise Exception('Unexpected exception was raised.')

# ItemExists returns true on existing name
exists = satellites.ItemExists(zeroth_satellite_name)
print(f'satellite \"{zeroth_satellite_name}\" exists: {exists}')

# ItemExists returns false on non-existent name
exists = satellites.ItemExists('07')
print(f'satellite \"07\" exists: {exists}')

# Basic Types
# Most of the ODTK attributes are simple scalar types that have equivalents in many programming
# languages: {REAL, INT, BOOL, STRING, STRING ENUMERATION}.

# Type REAL
# Real attributes are used for unit-less real numbers (min/max constraint may apply).

scenario.OrbitClassifications.LEO.EccentricityMax = 0.8
eccentricity_max = scenario.OrbitClassifications.LEO.EccentricityMax.eval()
print(f'Eccentricity max: {eccentricity_max}')

# Type INT
# These attributes are for integer values (min/max constraint may apply).

scenario.Measurements.LookAheadBufferSize = 200
look_ahead_buffer_size = scenario.Measurements.LookAheadBufferSize.eval()
print(f'Measurements look ahead buffer size: {look_ahead_buffer_size}')

# Type BOOL
# Boolean attributes accept values of true and false.

filter1 = scenario.Filter['Filter1']
filter1.Output.SmootherData.Generate = True
generate = filter1.Output.SmootherData.Generate.eval()
print(f'Generate: {generate}')

# Type STRING
# An example of a string is a "Description" field available on all ODTK objects.

scenario.Description = 'This is an example ...'
scenario_description = scenario.Description.eval()
print(f'Scenario description: {scenario_description}')

# Type STRING ENUMERATION
# This type of STRING attribute can only accept a specific pre-defined set of values. For
# instance, Filter.StartMode can be either "Initial", "Restart", or "AutoRestart".
if filter1.ProcessControl.StartMode.eval() == 'Initial':
    filter1.ProcessControl.StartMode = 'AutoRestart'
print(f'Filter process control start mode: {filter1.ProcessControl.StartMode.eval()}')

# Use the "Choices" property to get the list of valid enumeration choices
for start_mode in filter1.ProcessControl.StartMode.Choices:
    print(f'Start mode: {start_mode.eval()}')

# One special case of the string enumeration is the SelectedRestartTime for a filter or simulator.
# The choices in this case change based on each filter or simulator run, and the choices contain a list of date/time
# strings with units of UTCG or GPSG. The units are determined by the scenario date units setting
# scenario.Units.DateFormat.
# When setting the SelectedRestartTime in a script, any of the following formats will work; if no units are defined,
# the input date string will be assumed to be in the scenario units. If the restart time that you set is not a valid
# restart time, then the SelectedRestartTime will not be set.

simulator = odtk.application.createObj(scenario, 'Simulator', 'Simulator1')
tracking_system = odtk.application.createObj(scenario, 'TrackingSystem', 'TrackingSystem1')
facility = odtk.application.createObj(tracking_system, 'Facility', 'Facility1')

if not simulator.Go():
    print('Simulator run failed.')
    exit()
filter1.ProcessControl.StartMode = 'Initial'
if not filter1.Go():
    print('Filter run failed.')
    exit()

last_selected_restart_time = ''
print('Selected restart time choices')
for selected_restart_time in filter1.ProcessControl.SelectedRestartTime.Choices:
    last_selected_restart_time = selected_restart_time.eval()
    print(f'   {last_selected_restart_time}')

print(f'Scenario default units are: {scenario.Units.DateFormat.eval()}')
print('SelectedRestartTime will be set to ' + last_selected_restart_time)
filter1.ProcessControl.SelectedRestartTime = last_selected_restart_time
print(f'SelectedRestartTime was set to {filter1.ProcessControl.SelectedRestartTime.eval()}')

# Compound Types
# OD Tool Kit uses a number of compound types that have special methods for handling Units, Dimensions,
# Date representations, and coordinate system transformations as well as standard containers such as lists and sets.

# Type QUANTITY

# Quantities are values that have an associated unit, such as: 1 sec, 5 km, and 3 rad/sec. Several methods and
# properties are available to work with the quantity attributes.

# The properties Unit and Dimension return the default unit and dimension.

print(f'Unit: {filter1.ProcessControl.TimeSpan.Unit.eval()}')
print(f'Dimension: {filter1.ProcessControl.TimeSpan.Dimension.eval()}')

# The methods GetIn() and Set() perform unit conversion based on the input unit.

filter1.ProcessControl.TimeSpan.Set(4, 'min')
print(f'{filter1.ProcessControl.TimeSpan.GetIn("min")} min')
print(f'{filter1.ProcessControl.TimeSpan.GetIn("sec")} sec')

# In addition to working with one of the scenario object quantities you can create a new quantity object with the
# ODTK.NewQuantity() function. The returned quantity object can be either assigned to one of the existing attributes
# or used to perform a unit conversion.

temp = odtk.NewQuantity(2, 'arcSec')
facility.MeasurementStatistics[2].Type.Bias = temp
tracking_system.IonosphereModel.TransmitFreq = odtk.NewQuantity(2100, 'MHz')
qty = odtk.NewQuantity(100, 'mi/hr')
kmSecQty = qty.GetIn('km/sec')
print(f'qty: {kmSecQty} km/sec')

# Type DATE

# Dates are treated similarly to Quantities. They have a Set() method to assign a value and a Format() method to
# retrieve the DateTime string in a specified format. You can create a new Date object using the odtk.NewDate()
# function. The first parameter is the value or string containing the date, the second parameter is one of the
# standard ODTK date formats.

jd1 = odtk.NewDate(1, 'JDate')
utcgDate = jd1.Format('UTCG')
print(f'JDate: {utcgDate}')

# The Set() function returns a handle to the Date object that is being modified. The input parameters are the same as
# the NewDate function.

filter1.ProcessControl.StartTime.Set(1, 'JDate')
start_time = filter1.ProcessControl.StartTime.Format('GPSG')
print(f'Start time: {start_time}')

# ODTK's Date object also implements three Date Time arithmetic methods, AddTime, SubtractTime, and SubtractDate.

d1 = filter1.ProcessControl.StartTime
d2 = filter1.ProcessControl.StopTime
d3 = d1.AddTime(odtk.NewQuantity(1, 'hr'))
d4 = d2.SubtractTime(odtk.NewQuantity(5, 'min'))
timeSpan = d4.SubtractDate(d3)
timeSpanMin = timeSpan.GetIn('min')
print(f'Time span: {timeSpanMin} min')

# In addition to arithmetic functions, these functions allow date comparison:
# Equals(), GreaterThan(), GreaterThanOrEqual(), Inequality(), LessThan(), LessThanOrEqual()

t1 = simulator.ProcessControl.StartTime
t2 = filter1.ProcessControl.StartTime

t1_utcg = t1.Format('UTCG')
print(f't1: {t1_utcg}')
t2_utcg = t2.Format('UTCG')
print(f't2: {t2_utcg}')
if t1.GreaterThan(t2):
    print('t1 > t2')
if t1.GreaterThanOrEqual(t2):
    print('t1 >= t2')
if t1.GreaterThanOrEqual(t1):
    print('t1 >= t1')
if t1.LessThanOrEqual(t1):
    print('t1 <= t1')
if t1.Equals(t1):
    print('t1 == t1')
if t1.Inequality(t2):
    print('t1 != t2')
if t2.LessThan(t1):
    print('t2 < t1')
if t2.LessThanOrEqual(t1):
    print('t2 <= t1')

# Date objects are often useful when converting date and time formats from other software or systems. At times it's
# useful to start up ODTK and use it as a crude data conversion utility! Sometimes the input format is not one that
# ODTK natively supports. However, a little judicious string manipulation can often reorganize the input date and
# time into something that ODTK can handle. For example, you may have a date and time format that consists of the
# year and the elapsed seconds since the beginning of the year (assumed to be 1 Jan 00:00:00 UTC), e.g. 2009/2560004.
#  You could rely on your own date conversion routines and worry about leap years and leap seconds. Or you could
# simply pass it into ODTK using something like the following and then request it back out in a different format.

test_date = odtk.NewDate("1 Jan 2009 00:00:256", "UTCG")
print(f"test_date: {test_date.Format('UTCG')}")
test_date = odtk.NewDate("001/2560004 2009", "GMT")
print(f"test_date: {test_date.Format('UTCG')}")

# Type LINKTO

# File and directory names are strings but they are validated during the assignment. The application makes sure that
# an input file exists, or an output file can be written. Otherwise it will generate an error and the new value will
# not be set:

try:
    # set non-existent file
    scenario.EarthDefinition.EOPFilename = 'C:\\Non-Existent-Folder\\none-existent-file.txt'
    raise Exception('The expected exception was not thrown.')
except ClientException as e:
    if e.error_code == ClientExceptionCodes.EXECUTION_ERROR and 'Cannot find file' in str(e):
        print('Non-existent file path threw an exception as expected.')
    else:
        raise Exception('Unexpected exception was raised.')

# Type LINKTO ENUMERATION

# Some objects have links to enumerated types such as the solar radiation pressure model or measurement bias model
# and are identified as having type "LINKTO ENUMERATION". These parameters have an extra attribute "Type" that is
# used to set and get their values.

satellite.ForceModel.SolarPressure.Model.Type = 'Spherical'
print(f'Solar pressure model: {satellite.ForceModel.SolarPressure.Model.Type.eval()}')

# currently doesn't work with ODTKRuntime (scenario.Measurements.Files is empty)
demonstrate_list = True

if demonstrate_list:
    # Type LIST

    # The List container holds an unordered list of simple types like STRINGs or INTs or compound objects. The
    # easiest way to identify what types of objects are in a list is to add an element through the user interface.
    # The columns in the list identify the names of each of the properties of the elements. Use the NewElem() method
    # to create a new object that can be added to the list. Actually adding it to the list is accomplished using
    # push_back(ne) or push_front(ne). The entire list can be cleared using clear() and the ith element removed using
    #  RemoveAt(i). The number of elements in the list is available using size(). Elements in the list can be
    # accessed by index number or by iterating through the list.
    measurement_files = scenario.Measurements.Files
    print(f'Measurement files count: {measurement_files.count}')
    measurement_file = measurement_files[0]
    measurement_file_name = measurement_file.FileName.value.eval()
    print(f'First measurement file: {measurement_file_name}')
    # Clear the list
    measurement_files.clear()
    print(f'Measurement files count: {measurement_files.count}')
    # Add a new item to it
    ne = measurement_files.NewElem()
    ne.Enabled = True
    ne.FileName = measurement_file_name
    measurement_files.push_back(ne)
    print(f'Measurement files count: {measurement_files.count}')
    # Walk through the list using indices
    for i in range(measurement_files.size.eval()):  # 'count' can also be used instead of 'size'
        print(f'Measurement file ({i}): {measurement_files[i].FileName.value.eval()}')
    # Walk through the list using iterators
    for file in measurement_files:
        print(f'Measurement file: {file.FileName.value.eval()}')

# Type SETLINKTOOBJ

# Some ODTK objects have a special container SetLinkToObj that acts like a Set (in that only unique items can be
# contained in it) and the unique items are links to other ODTK objects. A common example of this is a Filter
# object's SatelliteList. You can choose to add specific satellite objects into the SatelliteList, but you can only
# add the satellite once. Use the InsertbyName() method to add a new object into the list. Alternatively,
# you can retrieve the list in your script via the Choices property. The entire SetLinkToObj can be cleared using
# clear() and an individual element removed using erase(). The number of elements in the SetLinkToObj is available
# using size(). Elements in the SetLinkToObj can be accessed by index number or by iterating through the
# SetLinkToObj. The methods begin() and end() return iterators that have the following methods:
# IsSafeToDereference(), Dereference(), Increment(), and Decrement().

# Clear out the existing SatelliteList
filter1.SatelliteList.clear()

# Add a particular satellite called mySat
success = filter1.SatelliteList.InsertByName("mySat")
print(success)

# Iterate through the list of possible choices we could have used
for choice in filter1.SatelliteList.Choices:
    print(choice.eval())

# Add the 2nd satellite to the list (0 indexed)
filter1.SatelliteList.insert(filter1.SatelliteList.Choices[1])

# Remove mySat from the list
filter1.SatelliteList.erase("mySat")

# Type SET

# The Set container is similar to a list but is ordered by an internal constraint and will reject duplicates. Use the
#  NewElem() method to create a new object that can be added to the Set. Actually adding it to the list is
# accomplished using insert(ne). The entire Set can be cleared using clear() and an individual element removed using
# erase(). The number of elements in the Set is available using size(). Elements in the Set can be accessed by index
# number or by iterating through the Set. Some Sets such as MeasurementStatistics have additional methods that are
# useful such as InsertByName(string), RemoveByName(string), and FindByName(string) where string is the name of the
# element being inserted, found, or removed. InsertByName() and RemoveByName() return a boolean indicating whether
# the element was successfully added or removed. Not all sets implement FindByName() and RemoveByName(),
# only the more commonly used sets do.

# The methods begin(), end(), and FindByName() return iterators that have the following methods: IsSafeToDereference(),
# Dereference(), Increment(), and Decrement().

# Clear out the set
measurement_statistics = facility.MeasurementStatistics
measurement_statistics.clear()

# Add a range measurement model
success = measurement_statistics.InsertByName('Range')
print(f'Range measurement model added: {success}')
ms = measurement_statistics[measurement_statistics.count - 1]

ms.Type.BiasSigma.Set(10, 'm')
ms.Type.BiasHalfLife.Set(6, 'hr')
ms.Type.WhiteNoiseSigma.Set(4, 'm')

# Add an azimuth measurement model
success = measurement_statistics.InsertByName('Azimuth')
print(f'Azimuth measurement model added: {success}')
ms = measurement_statistics[measurement_statistics.count - 1]

ms.Type.BiasSigma.Set(0.1, 'deg')
ms.Type.BiasHalfLife.Set(6, 'hr')
ms.Type.WhiteNoiseSigma.Set(0.05, 'deg')

# Now remove the range model
success = measurement_statistics.RemoveByName('Range')
print(f'Range model removed: {success}')

# Special Cases

# Maneuver Sets

# -------------------------------------------------------
# Finite maneuver example
# -------------------------------------------------------

# Clear out any existing finite maneuvers and add a new
# one in.

finite_maneuvers = satellite.ForceModel.FiniteManeuvers
finite_maneuvers.clear()

# Create a new maneuver to model a cross-track delta-I
fm_iter = finite_maneuvers.InsertNew('FiniteManConstThrust')
if fm_iter.IsSafeToDereference():
    fm = fm_iter.Dereference()

    fm.Name = 'FMTest1'
    fm.Enabled = True
    fm.Frame = 'Gaussian (RIC)'
    fm.Estimate = 'MagnitudeAndPointing'

    # Configure the burn time
    fm.Time.StopMode = 'TimeSpan'
    fm.Time.StartTime.Set('1 Jun 2009 00:00:00', 'UTCG')
    fm.Time.TimeSpan.Set('45', 'min')

    # Configure the burn parameters
    fm.Thrust.Specification = 'ByComponent'
    fm.Thrust.ThrustX.Set(0, 'N')
    fm.Thrust.ThrustY.Set(0, 'N')
    fm.Thrust.ThrustZ.Set(2, 'lbf')

    # Configure the mass loss
    fm.Mass.LossMethod = 'BasedOnIsp'
    fm.Mass.Isp.Set(325.0, 'sec')

    # Configure the burn uncertainty
    fm.Uncertainty.Type = '%MagnitudeAndPointing'
    fm.Uncertainty.PercentMagnitudeSigma.Set(3.0, '%')
    fm.Uncertainty.PointingSigma.Set(1.5, 'deg')
    fm.Uncertainty.MagnitudeHalfLife.Set(1, 'hr')
    fm.Uncertainty.PointingHalfLife.Set(1, 'hr')

# Add in a second maneuver as a dummy maneuver just
# to prove that we can find the right maneuver
fm_iter = finite_maneuvers.InsertNew('FiniteManConstThrust')

if fm_iter.IsSafeToDereference():
    fm = fm_iter.Dereference()

    # We'll set the name and accept the defaults for all the
    # other parameters.
    fm.Name = 'FMTest2'

# Now try to find the first maneuver and report the
# thrust.

fm_iter = finite_maneuvers.FindByName('FMTest1')
if fm_iter.IsSafeToDereference():
    fm = fm_iter.Dereference()

    print(f'Found maneuver {str(fm.Name.eval())}\nThrust is {fm.Thrust.ThrustZ.GetIn("lbf")} lbf')

# Now delete the second maneuver

fm_iter = finite_maneuvers.FindByName('FMTest2')

if fm_iter.IsSafeToDereference():
    fm = fm_iter.Dereference()

    print(f'Found maneuver {fm.Name.eval()}\nThrust is {fm.Thrust.ThrustZ.GetIn("lbf")} lbf')

    finite_maneuvers.RemoveByName('FMTest2')

# Verify that the second maneuver is gone.

fm_iter = finite_maneuvers.FindByName('FMTest2')
if not fm_iter.IsSafeToDereference():
    print('Second maneuver was deleted')

# -------------------------------------------------------
# Impulsive maneuver example
# -------------------------------------------------------

# Clear out any existing instant maneuvers and add a new
# one in.

instant_maneuvers = satellite.ForceModel.InstantManeuvers
instant_maneuvers.clear()

# Create a new maneuver to model an in-track delta-V

im_iter = instant_maneuvers.InsertNew('InstantManDeltaV')

if im_iter.IsSafeToDereference():
    im = im_iter.Dereference()

    im.Name = 'IMTest1'
    im.Enabled = True
    im.Frame = 'Gaussian (RIC)'

    # Configure the burn time (assumes the actual burn is
    # 4 minutes long but is modeled as an impulsive burn)

    im.Epoch.Set('1 Jan 2009 01:23:45', 'UTCG')
    im.TimeAfterStart.Set(2, 'min')
    im.TimeBeforeEnd.Set(2, 'min')

    # Configure the burn parameters

    im.DeltaV.Specification = 'ByComponent'
    im.DeltaV.DeltaVX.Set(0.0, 'm/sec')
    im.DeltaV.DeltaVY.Set(0.1, 'm/sec')
    im.DeltaV.DeltaVZ.Set(0.0, 'm/sec')

    # Configure the mass loss

    im.Mass.LossMethod = 'Explicit'
    im.Mass.MassLoss.Set(1, 'kg')

    # Configure the burn uncertainty

    im.Uncertainty.Type = 'ByComponent'
    im.Uncertainty.XSigma.Set(0.01, 'm/sec')
    im.Uncertainty.YSigma.Set(0.02, 'm/sec')
    im.Uncertainty.ZSigma.Set(0.01, 'm/sec')

# Add in a second maneuver as a dummy maneuver just
# to prove that we can find the right maneuver

im_iter = instant_maneuvers.InsertNew('InstantManDeltaV')

if im_iter.IsSafeToDereference():
    im = im_iter.Dereference()

    # We'll set the name and accept the defaults for all the
    # other parameters.

    im.Name = 'IMTest2'

# Now try to find the first maneuver and report the delta-V

im_iter = instant_maneuvers.FindByName('IMTest1')
if im_iter.IsSafeToDereference():
    im = im_iter.Dereference()
    print(f'Found maneuver {im.Name.eval()}\nDelta-V is {im.DeltaV.DeltaVY.GetIn("m/sec")}m/sec')

# Now delete the second maneuver

im_iter = instant_maneuvers.FindByName('IMTest2')

if im_iter.IsSafeToDereference():
    print('Found second maneuver')

    instant_maneuvers.RemoveByName('IMTest2')

# Verify that it is gone.

im_iter = instant_maneuvers.FindByName('IMTest2')
if not im_iter.IsSafeToDereference():
    print('Second maneuver was deleted')


# Multiple representations: Facility.Position

# The Facility.Position is a multiple representation object. Changes must be applied to the entire scope at once to
# ensure the proper coordinate transformation. To do that, first get position elements in one of the available
# representations: ToCartesian(), ToGeodetic(), ToGeocentric(), ToCylindrical(), and ToSpherical(). Then modify
# individual elements of the temp variable and then assign them back at once.

def print_geodetic_pos(p):
    print(f'Lat : {p.Lat.GetIn("deg")} deg, Lon: {p.Lon.GetIn("deg")} deg, Alt: {p.Alt.GetIn("m")} m')


pos = facility.Position.ToGeodetic()
print_geodetic_pos(pos)

pos.Lat.Set(10, 'deg')
pos.Lon.Set(20, 'deg')
pos.Alt.Set(100, 'm')

facility.Position.Assign(pos)
pos = facility.Position.ToGeodetic()
print_geodetic_pos(pos)


# Multiple representations: Satellite.OrbitState

# Similarly Satellite.OrbitState's individual members defining the orbit state vector must be changed in a temp
# variable and then assigned back as a group.

def print_keplerian_orbit_state(orbit_state):
    print(f'Epoch : {orbit_state.Epoch.Format("UTCG")} UTCG, Eccentricity: {orbit_state.Eccentricity.eval()}, '
          f'TrueArgOfLatitude: {orbit_state.TrueArgOfLatitude.GetIn("deg")} deg, '
          f'Inclination: {orbit_state.Inclination.GetIn("deg")} deg, '
          f'RAAN: {orbit_state.RAAN.GetIn("deg")} deg, ArgOfPerigee: {orbit_state.ArgOfPerigee.GetIn("rad")} rad')


kep = satellite.OrbitState.ToKeplerian()
print_keplerian_orbit_state(kep)
# Raise altitude by 10 km

newSize = kep.SemiMajorAxis.GetIn('km')
kep.SemiMajorAxis.Set(newSize + 10, 'km')

# Set the rest of the orbital elements

kep.Epoch.Set('1 Jul 2009 00:00:00', 'UTCG')
kep.Eccentricity = 0.00123
kep.TrueArgOfLatitude.Set('33.3', 'deg')
kep.Inclination.Set('67.8', 'deg')
kep.RAAN.Set('321.123', 'deg')
kep.ArgOfPerigee.Set('3.141592654', 'rad')

kep = satellite.OrbitState.Assign(kep)
print_keplerian_orbit_state(satellite.OrbitState.ToKeplerian())

# Type LINKTOOBJ with "not specified" choice

# The LINKTOOBJ type is a pointer to a specific group of objects, which sometimes can offer a "not specified" choice.
# Examples are the GNSSReceiver.DefaultAntenna, Transponder.DefaultAntenna, and Facility.ReferenceEmitter attributes.

gpsr = odtk.application.createObj(satellite, 'GNSSReceiver', 'GNSSReceiver1')
antenna = odtk.application.createObj(gpsr, 'Antenna', 'Antenna1')
for choice in gpsr.DefaultAntenna.Choices:
    choiceVal = choice.eval()
    if type(choiceVal) == str:
        print(choiceVal)
    else:
        print(choiceVal.name.eval())

gpsr.DefaultAntenna = 'not specified'
print("Antenna 1: " + str(gpsr.DefaultAntenna.ID.eval()))
gpsr.DefaultAntenna = gpsr.Antenna[0]
print("Antenna 2: " + str(gpsr.DefaultAntenna.ID.eval()))


# Product Builder: Creating Reports and Graphs

# Building and Using a Data Product List

# The script example below assumes there is no existing data product list. So it builds a data product each time it
# is called to produce the desired output.

# Generic function to build and create a product.
def run_report(input_file_name, style_path, product_name, export_file_path):
    # Create a new data product at the end of the list

    new_elem = odtk.ProductBuilder.DataProducts.NewElem()
    odtk.ProductBuilder.DataProducts.push_back(new_elem)
    index = odtk.ProductBuilder.DataProducts.size.eval() - 1
    product = odtk.ProductBuilder.DataProducts[index]

    # Configure the the data product

    new_src = product.Inputs.DataSources.NewElem()
    product.Inputs.DataSources.push_back(new_src)

    product.Name.Assign(product_name)
    product.Inputs.DataSources[0].Filename = input_file_name
    product.Outputs.Style = style_path
    product.Outputs.Display = True

    product.Outputs.Export.Enabled = True
    product.Outputs.Export.Format = "CommaSeparated"
    product.Outputs.Export.FileName = export_file_path

    # Create the product

    if not odtk.ProductBuilder.GenerateProduct(product_name):
        raise Exception('GenerateProduct failed. Please check the log for more details.')

    print(f'{input_file_name} exported to {export_file_path}')


odtk.ProductBuilder.DataProducts.Clear()

archive_file_name = scenario.Filter[0].Output.DataArchive.Filename.value.eval()
print(f'Archive file: {archive_file_name}')
style_file_path = os.path.join(this_dir_path, "..", "SharedResources", "measHist.exp")
output_file_path = os.path.join(this_dir_path, "measHist.txt")
run_report(archive_file_name, style_file_path, "measHist", output_file_path)

# Setting a custom location for the ODTK log file

# By default ODTK will create its log in a user temp directory and delete it upon application exit.
# However, you may override this by using the following commands:

appendMode = True
log_file_path = os.path.join(this_dir_path, "log.txt")
odtk.Application.SetLogFile(log_file_path, appendMode)

log_level_debug = 0
log_level_info = 1
log_level_force_info = 2
log_level_warning = 3
log_level_error = 4

odtk.Application.LogMsg(log_level_info, f"LogFile = {odtk.Application.LogFile.eval()}")
odtk.Application.LogMsg(log_level_warning, "This is a warning message.")
odtk.Application.LogMsg(log_level_error, "This is an error message.")

# Using ODTK.WriteMessage() function

# WriteMessage works for desktop only; the Runtime accepts the command and returns true but does not write a message.

odtk.WriteMessage("Example error message...", "error")
odtk.WriteMessage("Example warning message...", "warn")
odtk.WriteMessage("Example forced message...", "force")
odtk.WriteMessage("Example info message...", "info")
odtk.WriteMessage("Example debug message...", "debug")
odtk.WriteMessage("Yawn", "sleep 1000")  # Causes system sleep for 1 sec
