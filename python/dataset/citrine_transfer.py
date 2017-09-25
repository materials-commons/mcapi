from pypif.pif import dumps
from pypif.obj.common import Property, Scalar, FileReference, ProcessStep, Method
from pypif.obj.common import Person, Name, Source, Reference, License, Value, Instrument
from pypif.obj.system.chemical import ChemicalSystem
from pypif.obj.system.chemical.common import Composition

from .public_connection import Public


class Citrine:

    def mc_dataset_to_pifs(self, dataset_id):
        public = Public()
        dataset = public.get_dataset(dataset_id)
        dataset_url = 'https://materialscommons.org/mcapp/#/data/dataset/' + dataset_id

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

        measurement_instrument = Instrument(
            name="EPMA SEM"
        )

        measurement_method = Method(
            name="EPMA SEM measurement",
            instruments=[measurement_instrument]
            # also software = [Software()] ??
        )

        data_supply_instrument = Instrument(
            name="Materials Commons Dataset",
            url=dataset_url
        )

        data_supply_method = Method(
            name="Download From Materials Commons Dataset",
            instruments=[data_supply_instrument]
            # also software = [Software()] ??
        )

        # Properties...

        grid_dimension = Property(
            name='measurement grid dimension',
            scalers=[Scalar(value=20), Scalar(value=20)],
            methods=[measurement_method]
        )

        casting_image_file = Property(
            name="Image of Casting (L124)",
            files=FileReference(
                url="http://mc.server.org/fileStore/MagicKey",
                mime_type="image/jpeg",
                sha256="hashcode"
            ),
            methods=[data_supply_method]
        )

        casting_description_file = Property(
            name="LIFT Specimen Die",
            files=FileReference(
                url="http://mc.server.org/fileStore/MagicKey",
                mime_type="image/jpeg",
                sha256="hashcode"
            ),
            methods=[data_supply_method]
        )

        sem_grain_size_image_file = Property(
            name="Grain Size EBSD from L380 comp at 5mm site",
            files=FileReference(
                url="http://mc.server.org/fileStore/MagicKey",
                mime_type="image/tiff",
                sha256="hashcode"
            ),
            methods=[data_supply_method]
        )

        sem_results_summary = Property(
            name="Experiment Data Lift380 L124 2016-12-27",
            files=FileReference(
                url="http://mc.server.org/fileStore/MagicKey",
                mime_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                sha256="hashcode"
            ),
            methods=[data_supply_method]
        )

        properties = [
            self.units_property('voltage', 'kv', 15, [measurement_method]),
            self.units_property('beam current', 'mA', 20, [measurement_method]),
            self.value_property('step size', 10, [measurement_method]),
            self.value_property('site description', 'on 5mm plate, center section, mid-thickness', [measurement_method]),
            grid_dimension, casting_image_file, casting_description_file, sem_results_summary
        ]

        properties.append('title',dataset.title)
        if dataset.description:
            properties.append('description',dataset.description)

        # Process Steps...

        casting_process_details = [
            self.value('casting generic category', "LIFT 389"),
            self.value('casting instance name', "L124"),
        ]

        sectioning_process_details = [
            self.value('sectioning properties', "Sectioning includes 5mm plate, center section")
        ]

        casting_process = ProcessStep(name="Obtaining casting of L124", details=casting_process_details)
        sectioning_process = ProcessStep(name="Sectioning l124", details=sectioning_process_details)

        # Other details...

        doi_reference = Reference(doi="fake doi")
        open_data_liscense = License(
            name=" ODC-BY 1.0",
            description="Open Data Commons Attribution, version 1.0",
            url="https://opendatacommons.org/licenses/by/summary/"
        )
        contact = Person(name=Name(title="HRH", given="Test", family="User"), email="test@mc.org")

        names = []
        for key in materials_commons_properties.keys():
            names.append(materials_commons_properties[key])

        # Put it all together... BTW: every object has tags = [string]

        pif = ChemicalSystem()
        pif.names = names
        pif.contacts = [contact]
        pif.chemicalFormula = "Not Sure What this is - need to find out!"
        pif.composition = composition = [composition_al, composition_ca, composition_zr]
        pif.source = Source(producer="LIFT Materials")
        pif.properties = properties
        pif.preperation = [casting_process, sectioning_process]
        pif.references = [doi_reference]
        pif.licenses = [open_data_liscense]

        d = dumps(pif, indent=4)
        print(d)

        return pif

    def value(self, name, n):
        return Value(name=name, scalars=[Scalar(value=n)])

    def value_unit(self, name, n, units):
        return Value(name=name, units=units, scalars=[Scalar(value=n)])


    def value_property(self, name, n, methods):
        return Property(
            dataType="EXPERIMENTAL",
            name=name,
            methods=methods,
            scalars=[Scalar(value=n)])


    def units_property(self, name, units, n, methods):
        return Property(
            dataType="EXPERIMENTAL",
            name=name,
            methods=methods,
            units=units,
            scalars=[Scalar(value=n)])
