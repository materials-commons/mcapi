import json
from pypif.pif import dumps
from pypif.obj.system import System
from pypif.obj.common import Property, Scalar, FileReference
from pypif.obj.system.chemical.alloy import Alloy
from pypif.obj.system.chemical.common import Composition

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

sample_properties = [
    Property(
        name  = "Example File",
        files = FileReference(
            url="http://mc.server.org/fileStore/MagicKey",
            mime_type="mime/type",
            sha256="hashcode"
        )
    )
]

source_

pif = System()
pif.uid = "foo"
pif.sample = Alloy(
    uuid       = 'alloy uuid',
    names      = ["Casting L124"],
    ids        = ["uuid L124 casting"],
    source     = "LIFT Casting",
    composition= [composition_al,composition_ca,composition_zr],
    properties = sample_properties
)
d = dumps(pif,indent=4)
print(d)
