"""Create a control rig to deform an eyelid with joints"""
import maya.cmds as cmds
import maya.api.OpenMaya as om
from typing import Optional

from eyelid_builder import common as eyelid_common


def _place_locator_at_center(eyeball: str, center_loc_grp: str, name: str) -> str:
    '''
    Place a locator at the center of eyeball, use this location to place joint center.
    
    Returns:
        str: center_locator.
    '''
    center = cmds.cluster(eyeball)
    center_locator = cmds.spaceLocator(n=f'{name}_centerLocator')
    cmds.matchTransform(center_locator, center)
    cmds.delete(center)
    cmds.parent(center_locator, center_loc_grp)
    cmds.hide(center_locator)

    return center_locator


def _eyelid_aim(joints: list[str], center_loc_grp: str, center_locator_pos: list[float], name: str) -> list[str]:
    '''
    Create upvector locator to eyeball, create locator in every joints position 
    then aim constraint locators and joints.
    
    Returns:
        list: locators created
    '''

    #create upvector locator from center locator
    up_loc = cmds.spaceLocator(name=f'{name}_upCenter_loc', position=center_locator_pos)[0]
    cmds.hide(up_loc)
    cmds.xform(up_loc, translation=center_locator_pos)
    cmds.move(0,2,0)
    cmds.parent(up_loc, center_loc_grp)

    loc_grp = cmds.createNode("transform", name=f'{name}_locs_grp', skipSelect=True)
    locs = []

    for i, joint in enumerate(joints):
        #create locator matching joint position
        jt_position = cmds.xform(joint, query=True, worldSpace=True, translation=True)
        loc = cmds.spaceLocator(name=f'{name}{i}_loc')[0]
        locs.append(loc)
        cmds.xform(loc, worldSpace=True, translation=jt_position, scale=(.2, .2, .2))
        jt_parent = cmds.listRelatives(joint, parent=True)[0]
        #aim constraint
        cmds.aimConstraint(loc, jt_parent, maintainOffset=True, weight=True, aimVector=(1,0,0), upVector=(0,1,0), worldUpType="object", worldUpObject=up_loc)
        cmds.parent(loc, loc_grp)

    cmds.hide(locs)
    return locs


def _eyelid_jt(vertices: list[str], name: str, center_locator: str) -> list[str]:
    '''
    Create joint at each selected vertices: list[str] position, 
    plus a center joint at the eyeball center, then parent.

    Returns:
        list: joints created
    '''
    center_locator_pos = cmds.xform(center_locator, query=True, worldSpace=True, translation=True)
    jt_grp = cmds.createNode("transform", name=f'{name}_joints_grp')
    joints = []

    for i, vertex in enumerate(vertices):
        vertex_pos = cmds.xform(vertex, query=True, worldSpace=True, translation=True)
        joint = cmds.createNode('joint', name=f'{name}{i}_jt', skipSelect=True)
        joints.append(joint)
        cmds.xform(joint, translation=vertex_pos)
        center_joint = cmds.createNode('joint', name=f'{name}{i}Center_jt', skipSelect=True, parent=jt_grp)
        cmds.xform(center_joint, translation=center_locator_pos)
        cmds.parent(joint, center_joint)
        cmds.joint(center_joint, edit=True, oj="xyz", secondaryAxisOrient="yup", children=True, zso=True)

    return joints


def _eyelid_curve(locs: list, crv_grp: str, name: str) -> str:
    '''
    Get locs position, then create a curve through theses points,
    then get u parameter of points on curve and connect poci parameter 
    to u parameter and locs translate.

    Returns:
        str: curve freshly created
    '''
    locs_points = [cmds.xform(loc, query=True, worldSpace=True, translation=True) for loc in locs]
    #create curve, rebuild from 0 to 1 data then get u param
    crv = cmds.curve(ep=locs_points, name=f'{name}_crv')
    cmds.parent(crv, crv_grp)
    cmds.xform(crv, centerPivots=True)
    cmds.rebuildCurve(crv, constructionHistory=0, rpo=1, rt=0, end=1, kr=0, kep=1, s=4)
    curve_dp = om.MGlobal.getSelectionListByName(crv).getDagPath(0)
    curve_fn = om.MFnNurbsCurve(curve_dp)
    cmds.hide(crv)

    for i, loc_position in enumerate(locs_points):
        #  get the u parameter of locs
        maya_loc_position = om.MPoint(loc_position)
        _, u = curve_fn.closestPoint(maya_loc_position)
        poci = cmds.createNode('pointOnCurveInfo', skipSelect=True)
        cmds.connectAttr(f'{crv}.ws', f'{poci}.inputCurve')
        cmds.setAttr(f'{poci}.parameter', u)
        cmds.connectAttr(f'{poci}.position', f'{locs[i]}.t')

    return crv


def _eyelid_blink(eye_ctl: str, crv_up: str, crv_down: str, name: str):
    '''
    Create eyelid controler with 'blink' and 'midPoint' attributes
    using average curves and blendshapes.

    Args:
        eye_ctl (str): control object used for the global attributes
        crv_up (str): up curve of the setup
        crv_down (str): down curve of the setup
        name (str): used as a base for the nodes created here
    '''
    if not cmds.attributeQuery('Blink', node=eye_ctl, exists=True):
        cmds.addAttr(eye_ctl, longName='Blink', keyable=True, defaultValue=0, minValue=0, maxValue=1)

    if not cmds.attributeQuery('MidPoint', node=eye_ctl, exists=True):
        cmds.addAttr(eye_ctl, longName='MidPoint', keyable=True, defaultValue=.5, minValue=0, maxValue=1)
    
    crv_dp_up = cmds.duplicate(
        crv_up, name=f'{name}eyelidUpStatic_crv', renameChildren=True
    )
    crv_static_up = cmds.listRelatives(crv_dp_up, shapes=True)
    crv_dp_down = cmds.duplicate(
        crv_down, name=f'{name}eyelidDownStatic_crv', renameChildren=True
    )
    crv_static_down = cmds.listRelatives(crv_dp_down, shapes=True)
    crv_dp_mid = cmds.duplicate(
        crv_dp_down, name=f'{name}eyelidMidPoint_crv', renameChildren=True
    )
    crv_mid_point = cmds.listRelatives(crv_dp_mid, shapes=True)
    cmds.hide(crv_dp_up, crv_dp_down, crv_dp_mid)

    # avg curve avec les 2 statics
    avg = cmds.createNode('avgCurves', skipSelect=True)
    cmds.setAttr(f'{avg}.automaticWeight', 0)
    cmds.connectAttr(f'{crv_static_up[0]}.ws', f'{avg}.inputCurve1')
    cmds.connectAttr(f'{crv_static_down[0]}.ws', f'{avg}.inputCurve2')
    cmds.connectAttr(f'{avg}.outputCurve', f'{crv_mid_point[0]}.create')

    # floatmath + blendshape
    float_node = cmds.createNode('floatMath', skipSelect=True)
    cmds.setAttr(f'{float_node}.operation', 1)  # subtract
    cmds.connectAttr(f'{eye_ctl}.MidPoint', f'{float_node}.floatB')
    cmds.connectAttr(f'{float_node}.floatB', f'{avg}.weight1')
    cmds.connectAttr(f'{float_node}.outFloat', f'{avg}.weight2')

    #blendshapes
    blendshape1 = cmds.blendShape(crv_mid_point, crv_up)
    cmds.connectAttr(f'{eye_ctl}.Blink', f'{blendshape1[0]}.{crv_mid_point[0]}')
    blendshape2 = cmds.blendShape(crv_mid_point, crv_down)
    cmds.connectAttr(f'{eye_ctl}.Blink', f'{blendshape2[0]}.{crv_mid_point[0]}')


@eyelid_common.undo_chunk
def do_it(
    eyeball: str, vertexUp: list[str], vertexDown: list[str], 
    name: str, eye_ctl: str, object_side: Optional[str]=None
):
    '''
    Create a joint for each vertex, parent to center, orient joint.
    TODO
        - invisible
    
    Args: 
        eyeball: eye mesh. Make sure eyes are on separate mesh, 
            right and left mesh, and labelized correctly.
        vertex: up & down vertex of eyelid selection.
        /!/ vertex = 2 THINGS TO DO :
            - BEFORE selecting vertex, change the track selection order
                (see example below)
            - DO NOT forget the flatten option in the ls command
                (see example below)
        eye_ctl: the existing eye controler
    
    Example:
        cmds.selectPref(trackSelectionOrder=True)
        #/!/ select your vertices only now, not before changing the trackSelectionOrder
        vertexUp = cmds.ls(os=True, fl=True)
        #Then
        vertexDown = cmds.ls(os=True, fl=True)
        eyelid.eyelid_gen(eyeball='L_cornea_msh', vertexUp=vertexUp, vertexDown=vertexDown, name='eyelid')
    '''

    if object_side is None:
        name = name
    else:
        name = f'{object_side}_{name}'

    crv_grp = cmds.createNode("transform", name=f'{name}_curves_grp', skipSelect=True)
    center_loc_grp = cmds.createNode("transform", name=f'{name}_centerLocs_grp', skipSelect=True)

    center_locator = _place_locator_at_center(eyeball, center_loc_grp, name=name)
    center_locator_pos = cmds.xform(center_locator, query=True, worldSpace=True, translation=True)

    joints_up   = _eyelid_jt(vertices=vertexUp, name=f'{name}Up', center_locator=center_locator)
    joints_down = _eyelid_jt(vertices=vertexDown, name=f'{name}Dn', center_locator=center_locator)
    locs_up     = _eyelid_aim(joints_up, center_loc_grp, center_locator_pos, name=f'{name}Up')
    locs_down   = _eyelid_aim(joints_down, center_loc_grp, center_locator_pos, name=f'{name}Dn')
    crv_up      = _eyelid_curve(locs_up, crv_grp, name=f'{name}Up')
    crv_down    = _eyelid_curve(locs_down, crv_grp,name=f'{name}Dn')
    eyelid_bs   = _eyelid_blink(eye_ctl, crv_up, crv_down, name)

    return eyelid_bs