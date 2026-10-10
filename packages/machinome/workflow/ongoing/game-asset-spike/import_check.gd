extends SceneTree
# Spike helper, run headless:
#   godot --headless --path <this dir> --script import_check.gd -- /abs/path/thor.glb
# Loads the GLB at runtime with Godot's own glTF importer, generates the scene,
# and reports the node tree, meshes, animations and the joint extras it kept.

func _init():
	var args := OS.get_cmdline_user_args()
	var path: String = args[0]
	var doc := GLTFDocument.new()
	var state := GLTFState.new()
	var err := doc.append_from_file(path, state)
	if err != OK:
		print("GODOT_REPORT ", JSON.stringify({"error": err}))
		quit(1)
		return
	var root := doc.generate_scene(state)
	var report := {"nodes": 0, "mesh_instances": 0, "triangles": 0, "animations": [], "joint_chain": [], "extras_on_root": false, "joint_extras": {}}
	_walk(root, report)
	for name in ["shoulder", "art2", "art3", "art4", "art56", "output"]:
		var n := root.find_child(name, true, false)
		report["joint_chain"].append({"name": name, "present": n != null, "descendants": _count(n) if n != null else null})
	var players := root.find_children("*", "AnimationPlayer", true, false)
	for p in players:
		for a in (p as AnimationPlayer).get_animation_list():
			report["animations"].append(a)
	# the extras travel as metadata on the generated nodes
	var top := root.get_child(0) if root.get_child_count() > 0 else root
	report["extras_on_root"] = top.has_meta("extras") or root.has_meta("extras")
	var art2 := root.find_child("art2", true, false)
	if art2 != null and art2.has_meta("extras"):
		report["joint_extras"] = art2.get_meta("extras")
	print("GODOT_REPORT ", JSON.stringify(report))
	quit()

func _walk(n: Node, report: Dictionary) -> void:
	report["nodes"] += 1
	if n is MeshInstance3D:
		report["mesh_instances"] += 1
		var mesh: Mesh = (n as MeshInstance3D).mesh
		if mesh != null:
			for s in range(mesh.get_surface_count()):
				var arrays := mesh.surface_get_arrays(s)
				var idx = arrays[Mesh.ARRAY_INDEX]
				report["triangles"] += (idx.size() / 3) if idx != null else (arrays[Mesh.ARRAY_VERTEX].size() / 3)
	for c in n.get_children():
		_walk(c, report)

func _count(n: Node) -> int:
	var total := 0
	for c in n.get_children():
		total += 1 + _count(c)
	return total
