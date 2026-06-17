"""Run once to generate tests/fixtures/sample.ifc"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import ifcopenshell
import ifcopenshell.api


def create_sample_ifc(output_path: str):
    f = ifcopenshell.file(schema="IFC4")

    # IfcProject must exist before unit.assign_unit can run
    project = ifcopenshell.api.run("root.create_entity", f, ifc_class="IfcProject", name="Test Project")
    ifcopenshell.api.run("unit.assign_unit", f)
    site = ifcopenshell.api.run("root.create_entity", f, ifc_class="IfcSite", name="Test Site")
    building = ifcopenshell.api.run("root.create_entity", f, ifc_class="IfcBuilding", name="Test Building")
    storey_gf = ifcopenshell.api.run("root.create_entity", f, ifc_class="IfcBuildingStorey", name="Ground Floor")
    storey_1f = ifcopenshell.api.run("root.create_entity", f, ifc_class="IfcBuildingStorey", name="First Floor")

    # In IfcOpenShell 0.8.x, aggregate.assign_object uses products= (list), not product=
    ifcopenshell.api.run("aggregate.assign_object", f, relating_object=project, products=[site])
    ifcopenshell.api.run("aggregate.assign_object", f, relating_object=site, products=[building])
    ifcopenshell.api.run("aggregate.assign_object", f, relating_object=building, products=[storey_gf, storey_1f])

    wall1 = ifcopenshell.api.run("root.create_entity", f, ifc_class="IfcWall", name="Wall 001")
    wall2 = ifcopenshell.api.run("root.create_entity", f, ifc_class="IfcWall", name="Wall 002")
    door1 = ifcopenshell.api.run("root.create_entity", f, ifc_class="IfcDoor", name="Door 001")

    # In IfcOpenShell 0.8.x, spatial.assign_container uses products= (list), not product=
    ifcopenshell.api.run("spatial.assign_container", f, relating_structure=storey_gf, products=[wall1, wall2, door1])

    pset = ifcopenshell.api.run("pset.add_pset", f, product=wall1, name="Pset_WallCommon")
    ifcopenshell.api.run("pset.edit_pset", f, pset=pset, properties={
        "IsExternal": True,
        "FireRating": "REI60",
    })

    qto = ifcopenshell.api.run("pset.add_qto", f, product=wall1, name="Qto_WallBaseQuantities")
    ifcopenshell.api.run("pset.edit_qto", f, qto=qto, properties={
        "Length": 5.0,
        "Height": 3.0,
        "Width": 0.2,
    })

    f.write(output_path)
    print(f"Written: {output_path}")


if __name__ == "__main__":
    out = Path(__file__).parent / "fixtures" / "sample.ifc"
    out.parent.mkdir(exist_ok=True)
    create_sample_ifc(str(out))
