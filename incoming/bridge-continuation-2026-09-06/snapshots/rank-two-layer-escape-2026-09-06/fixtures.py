"""Exact controls. Rational parameters, not floating-point approximations."""
from fractions import Fraction as Q
from itertools import product
from geometry import Geometry, unit, jsonable


def third_nearest_squared(g: Geometry):
    if g.n < 4:
        raise ValueError('Third-nearest assignment needs at least four points.')
    return [sorted(g.d2[i][j] for j in range(g.n) if j != i)[2] for i in range(g.n)]


def five_point_escape():
    return {'name': 'five_point_four_target_equality',
            'points': [(0,0),('24/25','7/25'),('3/5','4/5'),
                       ('-3/5','4/5'),('-24/25','7/25')],
            'radii_squared': [1,'338/125','36/25','36/25','338/125'],
            'note': 'Reused rank-two control from the preceding rank-one packet; not globally rich.'}


def double_star(a='3/4', b=3, c=20):
    left = [unit(t) for t in (a,b,c)]
    return [(Q(0),Q(0)), (Q(1),Q(0))] + left + [(1-x,y) for x,y in left]


def eight_point_exports():
    return {'name': 'eight_point_six_export_equality', 'points': double_star(),
            'radii_squared': [1,1,'162/125','162/125','23716/10025',
                              '162/125','162/125','23716/10025'],
            'note': 'Two rich minimum-radius centers and exactly six exported incidences; not globally rich.'}


def nine_point_return():
    source = (Q(0),Q(0))
    w = [unit(t) for t in ('1/4','1/3','10/7',39)]
    q = tuple(2*x for x in unit(29))
    v = [(q[0]+2*x,q[1]+2*y) for x,y in
         [unit(t) for t in ('16/5','22/3','19/3')]]
    return {'name': 'nine_point_rational_return', 'points': [source]+w+[q]+v,
            'radii_squared': [1,'4356/2533','1058/745','1058/745',
                              '138338/113389',4,4,4,4],
            'source': 0, 'return_center': 5,
            'coordinate_parameters': {'unit_parameterization':
                'u(t)=((1-t^2)/(1+t^2),2t/(1+t^2))',
                'minimum_witness_parameters': ['1/4','1/3','10/7','39'],
                'return_center': '2*u(29)',
                'return_witnesses': ['q+2*u(16/5)','q+2*u(22/3)','q+2*u(19/3)']},
            'note': 'The whole minimum layer is rich; deleting it destroys the only rich class at a higher center. Seven vertices are not rich.'}


def fixed_radius_controls():
    return [
      {'name':'one_point', 'points':[(0,0)], 'thresholds_squared':[1]},
      {'name':'two_points','points':[(0,0),(1,0)], 'thresholds_squared':['1/2',1,2]},
      {'name':'equilateral_triangle','points':[(0,0),(1,0),('1/2','1/2')],
       'vertical_scale_squared':3, 'thresholds_squared':[1,2]},
      {'name':'equilateral_rhombus','points':[(0,0),(1,0),('1/2','1/2'),('1/2','-1/2')],
       'vertical_scale_squared':3,'thresholds_squared':[1]},
      {'name':'square_closed_disk_boundary','points':[(0,0),(1,0),(1,1),(0,1)],
       'thresholds_squared':[1,2]},
      {'name':'regular_hexagon','points':[(1,0),('1/2','1/2'),('-1/2','1/2'),
                         (-1,0),('-1/2','-1/2'),('1/2','-1/2')],
       'vertical_scale_squared':3,'thresholds_squared':[1,3]},
      {'name':'obtuse_short_triangle','points':[(0,0),(3,0),(1,1)],
       'thresholds_squared':[10]},
      {'name':'right_short_triangle','points':[(0,0),(3,0),(0,4)],
       'thresholds_squared':[26]},
      {'name':'acute_short_triangle','points':[(0,0),(2,0),(1,2)],
       'thresholds_squared':[6]},
    ]


def all_controls():
    return fixed_radius_controls() + [five_point_escape(),eight_point_exports(),nine_point_return()]
