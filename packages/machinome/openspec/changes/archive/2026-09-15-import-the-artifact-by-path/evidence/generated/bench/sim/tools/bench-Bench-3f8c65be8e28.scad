union() {
	import(file = "../parts-RigidLeaf-5c13fc621640.stl", origin = [0, 0]);
	translate(v = [20, 0, 0]) {
		import(file = "../parts-ExactLeaf-d20b313b0496.stl", origin = [0, 0]);
	}
	translate(v = [40, 0, 0]) {
		import(file = "parts-FlexLeaf-a286075d8c7e-b4c4c1059a7c.stl", origin = [0, 0]);
	}
}
