import json
from pypif.pif import dumps
from pypif.obj.common import Property, Scalar, FileReference, ProcessStep, Method
from pypif.obj.common import Person, Name, Source, Reference, License, Value, Instrument
from pypif.obj.system.chemical import ChemicalSystem
# from pypif.obj.system.chemical.alloy import Alloy
from pypif.obj.system.chemical.common import Composition

def single_value(name, n):
    return Value(name=name, scalars=[Scalar(value=n)])

def single_units_value(name, units, n):
    return Value(name=name, units=units, scalars=[Scalar(value=n)])

## Parts...

materials_commons_global_properties = {
    'dataset_name': "Demo Project",
    'dateset_description': "Demo Project Description"
}

composition_al = Composition(
    element='Al',
    ideal_atomic_percent=Scalar(value=94)
)

composition_ca = Composition(
    element='Ca',
    ideal_atomic_percent=Scalar(value=1)
)

composition_zr = Composition(
    element='Zr',
    ideal_atomic_percent=Scalar(value=5)
)

measurement_setup_values = [
    single_units_value('voltage', 'kv', 15),
    single_units_value('beam current', 'mA', 20),
    single_value('step size', 10),
    Value(name='grid dimension', scalers=[Scalar(value=20),Scalar(value=20)]),
    single_value('site description', 'on 5mm plate, center section, mid-thickness')
]

casting_image_file = Property(
    name  = "Image of Casting (L124)",
    files = FileReference(
        url="http://mc.server.org/fileStore/MagicKey",
        mime_type="image/jpeg",
        sha256="hashcode"
    )
)

casting_description_file = Property(
    name = "LIFT Specimen Die",
    files = FileReference(
        url="http://mc.server.org/fileStore/MagicKey",
        mime_type="image/jpeg",
        sha256="hashcode"
    )
)

sem_grain_size_image_file = Property(
    name = "Grain Size EBSD from L380 comp at 5mm site",
    files = FileReference(
        url="http://mc.server.org/fileStore/MagicKey",
        mime_type="image/tiff",
        sha256="hashcode"
    )
)

sem_results_summary = Property(
    name = "Experiment Data Lift380 L124 2016-12-27",
    files = FileReference(
        url="http://mc.server.org/fileStore/MagicKey",
        mime_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        sha256="hashcode"
    )
)

measurement_instrument = Instrument(
    name = "name",
    model = "model",
    producer = "producer",
    url = "url"
)

measurement_method = Method(
    name="EPMA SEM",
    instruments = [measurement_instrument],
    # also software = [Software()] ??
)

measured_property = Property(
    dataType = "EXPERIMENTAL",
    methods = [measurement_method]
)

casting_process_details = [
    single_value('casting generic category', "LIFT 389"),
    single_value('casting instance name',"L124"),
]

sectioning_process_details = [
    single_value('sectioning properties',"Sectioning includes 5mm plate, center section")
]

measurement_process_details = measurement_setup_values

casting_process = ProcessStep(name="Obtaining casting of L124", details=casting_process_details)
sectioning_process = ProcessStep(name="Sectioning l124", details=sectioning_process_details)
measurement_process = ProcessStep(
    name = "EPMA SEM",
    details = measurement_process_details,
    instruments=[measurement_instrument]
    # also software = [Software()] ??
)

doi_reference = Reference(doi="fake doi")
open_data_liscense = License(
    name=" ODC-BY 1.0",
    description="Open Data Commons Attribution, version 1.0",
    url="https://opendatacommons.org/licenses/by/summary/"
)
contact = Person(name=Name(title="HRH",given="Test",family="User"),email="test@mc.org")

## Put it all together... BTW: every object has tags = [string]

pif = ChemicalSystem()
pif.names = [
    "Experiment Name", "Measurement of LIFT380 casting L124"
]
pif.contacts = [contact]
pif.chemicalFormula = "Not Sure What this is - need to find out!"
pif.composition = composition= [composition_al,composition_ca,composition_zr]
pif.source = Source(producer="LIFT Materials")
pif.properties = [casting_image_file, casting_description_file, sem_results_summary, measured_property]
pif.preperation = [casting_process, sectioning_process, measurement_process]
pif.references = [doi_reference]
pif.licenses = [open_data_liscense]

d = dumps(pif,indent=4)
print(d)
