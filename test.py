# Plate with a hole
import job
import mesh
from importlib.metadata import distribution
import multiprocessing
from tkinter import Variable
import part
import sketch
import step
import assembly
import section
import material
from msilib.schema import tables
from abaqus import*
from abaqusConstant import*
import regionToolsets
session.viewports[name].setValues(displayedObject=object)

# ------------------------------------------------------------------------------------------

# Create the model
# referring the object by key
mdb.Models.changeKey(fromName='name', toName='new name')
myModel = mdb.Model(name='Model A')
#myModel= beam/plate
# ------------------------------------------------------------------------------------------

# Create the part


# a) Sketch the model
mySketch = myModel.ConstrainedSketch(name='Sketch A', sheetSize=200.0)
mySketch.rectangel(point1=(x1, y1), point1=(x2, y2))

# b)Create a 3D deformable part
myPart = myModel.Part = (name='Part A', dimensionality=THREE_D, type=DEFORMABLE_BODY)
myPart.BaseSolid.Extrude(sketch=mySketch, depth=z)

# ------------------------------------------------------------------------------------------

# Create Material

# Create material by properties like mass,density,youngs modulus,possions ratio
myMaterial = myModel.Material(name='---steel')
myMaterial.Density(table=((,),))
myMaterial.Elastic(type=ISOTROPIC, table=((, ), ))

# ------------------------------------------------------------------------------------------

# Create Solid Section and assign the model(beam/plate) to it


# Create a section to assign to the model , name section = beam/plate section
mySection = myModel.HomogeneousSolidSection(
    name='name section', material=' AISI 1005 steel etc..')

# Assign the model to this section
my_region = (myPart.cells,)
myPart.SectionAssignment(region=my_region, sectionName='Name Section')

# ------------------------------------------------------------------------------------------

# Create the assembly


# Create the part instance
# mdb.Models[name].rootAssembly
myAssembly = myModel.rootAssembly
# A dependent instance is only a pointer to the geometry of the original part.
myInstance = myAssembly.Instance(
    name='Name Instance', part=myPart, dependent=ON)

# ------------------------------------------------------------------------------------------

# Create the step


# Create a static general step
myModel.StaticStep(name='Apply Load', pervious='Initial',
                   desciption='Load is applied during this step')

# ------------------------------------------------------------------------------------------

# Create the field output request

# Change the name of field output request 'F-Output-1' to 'Selected field Outputs'
myModel.fieldOutputrequest.changeKey(
    fromName='F-Output-1', toName='Selected Field Outputs')

# Since F-output-1 is applies at the 'Apply Load' step by default, 'Selected Outputs' will be too, We only need to set the required variables
myModel.fieldOutputRequests['Select Field Outputs'].setValues(
    variables=('S', 'E', 'PEMAG', 'U', 'RF', 'CF'))

# ------------------------------------------------------------------------------------------

# Create the history output request

# We try a slightly different method from that used in field output request
# Create a new history output request called 'Default History Outputs' and assign both the step and the variables
# History output is output defined for a single point or for values calculated for a portion of the model as a whole, such as energy.

myModel.HistoryOutputRequest(
    name='Default History Outputs', createStepName='Apply Load', variables=PRESELECT)

# now delete the original history output request 'H-Output-1'
del myModel, historyOutputRequest['H-Output-1']

# ------------------------------------------------------------------------------------------

# Apply Pressure load to top surface

# First we need to locate and select the top surface
# We pl

# Select faces using an arbitrary point on the face.

faceRegion = doorInstance.faces.findAt(
    ((30, 60, 1)))

# Create a surface containing the 1 face.
# Indicate which side of the surface to include.

mySurface = myModel.rootAssembly.Surface(
    name='exterior', side1Faces=faceRegion)

# selecting the face
top_face_region = regionToolsets.Region(side1Faces=faceRegion)

# Applying the pressure Load on this region in the 'Apply Load' step
myModel.Pressure(name='Uniform Applied Pressure', createSetpName='Apply Load',
                 region=top_face_region, distributionType=UNIFOREM, magnitude=10, amplitude=UNSET)

# ------------------------------------------------------------------------------------------

# Create the Mesh

Model_x_coord = x
Model_y_coord = y
Model_z_coord = z
elemType1 = mesh.ElemType(elemCode=C3D8R, elemLibrary=STANDARD, kinemarticSplit=AVERAGE_STRAIN,
                          secondOrderAccuracy=OFF, hourglassControl=DEFAULT, distortionControl=DEFAULT)
modelCells = modelPart.cells
selectedModelCells = modelCells.findAt(
    (Model_x_coord, Model_y_coord, Model_z_coord),)
ModelMeshRegion = (selectedModelCells,)
modelPart.setElementType(regions=beamMeshRegion, elemTypes=(elemType1,))
modelPart.seedPart(size=0.1, deviationFactor=0.1)
modelPart.generateMesh()

# ------------------------------------------------------------------------------------------

# Create and run the job

# Create the job
mdb.Job(name='Job Name', model='Model Name', type=ANALYSIS, explicitPrecision=SINGLE,
        nodalOutputPrecision=SINGLE, description='Job simulates a loaded model_name',
        parallelizationMethodExplicit=DOMAIN, multiprocessingMode=DEFAULT,
        numDomains=1, userSubsroutine='', numCpus=1, memory=50,
        memoryUnits=PERCEENTAGE, scratch='', eachPrint=OFF, modelPrint=OFF,
        contactPrint=OFF, historyPrint=OFF
        )

# Run the job
mdb.jobs['Job Name'].submit(consistencyChecking=OFF)

# Do not return controll till job is finished running
mdb.jobs['Job Name'].waitForCompletion()

# End of run job
# ------------------------------------------------------------------------------------------
