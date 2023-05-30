import * as THREE from './three.module.js';
import {TrackballControls} from './TrackballControls.js';
import {ParametricGeometries} from './ParametricGeometries.js';
import {get} from './urlvar/urlvar.mjs';

const MESHNUMBER = 10;

let camera, controls, scene, renderer;
let meshes, player;
let ambientLight, pointLight

init();
animate();

function init(
  meshNumber=MESHNUMBER,
  xSpread=1300,
  ySpread=1300,
  zSpread=500,
){
	camera = new THREE.PerspectiveCamera( 70, 1, 1, 10000 );
	camera.position.z = 400;
	scene = new THREE.Scene();
  meshes = [...Array(meshNumber)].map((_,i) => genMesh(i%2==0,Math.floor(1+i/2)));
	meshes.forEach(mesh => {
    mesh.rotation.x = 2 * Math.PI * Math.random();
    mesh.rotation.y = 2 * Math.PI * Math.random();
    mesh.rotation.z = 2 * Math.PI * Math.random();

    mesh.userData.pivot = new THREE.Group();
    mesh.userData.pivot.add(mesh);
    mesh.userData.pivot.position.x = -xSpread * Math.random() +xSpread/2;
    mesh.userData.pivot.position.y = -ySpread * Math.random() +ySpread/2;
    mesh.userData.pivot.position.z = -zSpread * Math.random() +zSpread/2 -1600;

    mesh.position.x = Math.random() * 1000 - 500;
    mesh.position.y = Math.random() * 1000 - 500;
    mesh.position.z = Math.random() * 1000 - 500;

    const rho = 0.0025
    const phi = Math.random()
    const psi = Math.random()
    mesh.userData.velocity = new THREE.Vector3(
      rho*Math.cos(phi)*Math.sin(psi),
      rho*Math.sin(phi)*Math.sin(psi),
      rho*Math.cos(psi)
    )

    scene.add( mesh.userData.pivot );
  })
	ambientLight = new THREE.AmbientLight( 0xffffff, 0.3 );
	scene.add( ambientLight );
	pointLight = new THREE.PointLight( 0xffffff, 0.7 )
	pointLight.position.set(200, 200, 200)
	scene.add(pointLight);
	player = new THREE.Mesh(
		new THREE.SphereBufferGeometry(5,10,10),
		new THREE.MeshBasicMaterial({color: 0xff0000})
	)
	player.position.set(-100,0,0);
	player.visible = false;
	scene.add(player);
	renderer = new THREE.WebGLRenderer( { antialias: true, preserveDrawingBuffer: true } );
	renderer.setPixelRatio( window.devicePixelRatio );
	renderer.physicallyCorrectLights = true;
	document.getElementById("preview").appendChild( renderer.domElement );
	controls = new TrackballControls( camera, renderer.domElement );
	controls.rotateSpeed = 1.0;
	controls.zoomSpeed = 1.2;
	controls.panSpeed = 0.8;
	rendererResize();
}

function animate(){
	requestAnimationFrame(animate);
  meshes.forEach(mesh => {
    mesh.userData.pivot.rotation.x += mesh.userData.velocity.x;
    mesh.userData.pivot.rotation.y += mesh.userData.velocity.y;
    mesh.userData.pivot.rotation.z += mesh.userData.velocity.z;
  })
	controls.update();
	renderer.render(scene, camera);
}

function rendererResize(
	width=window.innerWidth,
	height=window.innerHeight
){
	renderer.setSize( width, height );
	document.getElementById("preview").style.width = width+"px";
	document.getElementById("preview").style.height = height+"px";
	camera.aspect = width/height;
	camera.updateProjectionMatrix();
}

/**
 * Generate a Mesh corresponding to a topological 2-manifolg
 * @param {bool} orientable
 * @param {number} genus - (Demi-)Genus
 */
function genMesh(
	orientable=true,
	genus=1,
){
	const texture = new THREE.TextureLoader().load( './lib/submodules/top2manWebsiteBackground/res/texture.png' );
	texture.magFilter = THREE.NearestFilter;
	texture.minFilter = THREE.NearestFilter;
	const material = new THREE.MeshLambertMaterial( { map: texture } );
	//
	// Sphere
	if( orientable && genus==0 )
		return new THREE.Mesh(
			new THREE.SphereGeometry(100, 40, 40),
			material
		);
	// n-Torus
	else if( orientable && genus>=1 ){
		let mesh = new THREE.Group();
		let torus = new THREE.Mesh(
			new THREE.TorusGeometry( 100, 30, 16, 100 ),
			material
		);
		for(let i=0; i<genus; i++){
			let clone = torus.clone();
			clone.position.x = i*200-(genus-1)*100;
			clone.scale.y = (-1)**i
			mesh.add(clone)
		}
		// mesh.scale.set(1/Math.sqrt(genus),1/Math.sqrt(genus),1/Math.sqrt(genus))
		return mesh;
	}
	// Projektiver Raum
	else if( !orientable && genus==1 ){
		return new THREE.Mesh(
			new THREE.ParametricBufferGeometry(
				(u,v,target) => target.set(
					150*Math.cos(2*Math.PI*u)*Math.sin(Math.PI*v)/2,
					150*Math.sin(2*Math.PI*u)*Math.sin(Math.PI*v)/2,
					-100*(Math.cos(Math.PI/2*v)**2-Math.cos(2*Math.PI*u)**2*Math.sin(Math.PI/2*v)**2))/2
			, 110, 110 ),
			material
		)
	}
	// Kleinsche Flasche
	else if( !orientable && genus==2 ){
		let mesh = new THREE.Mesh(
			new THREE.ParametricBufferGeometry( ParametricGeometries.klein, 50, 50 ),
			material
		)
		material.side = THREE.DoubleSide;
		mesh.scale.set(15,15,15);
		return mesh
	}
	else if( !orientable && genus >2 ){
		let mesh = new THREE.Group();
		let a
		// Dycks Theorem
		if( genus%2 ){
			mesh.add(genMesh(true,Math.floor(genus/2)));
			a = genMesh(false,1);
			a.position.y = 150;
			a.position.z = 80;
		}
		else{
			mesh.add(genMesh(true,Math.floor(genus/2)-1));
			a = genMesh(false,2);
			a.rotateZ(Math.PI/2)
			a.position.y = 200;
		}
		if( Math.floor((genus+1)/2)%2 )
			a.position.x = 100;
		mesh.add(a)
		return mesh
	}
}

addEventListener( 'resize', () => rendererResize( window.innerWidth, window.innerHeight ) );
