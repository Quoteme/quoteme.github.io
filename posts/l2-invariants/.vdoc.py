# type: ignore
# flake8: noqa
from plotly.subplots import make_subplots
# the individual point we want to track under the action of the deck transformation
angle = np.pi*7/8
point = ( 
	np.cos(angle),
	np.sin(angle),
	angle/(2*np.pi)
 )
# group action. Because Z/3Z is cyclic, we only need to define the generator
g = lambda v: (v[0],v[1],v[2]+1 if v[2] < 2 else 0)

# covering [0]
fig = make_subplots(rows=1, cols=3, specs=[[{'type': 'scene'}, {'type': 'scene'}, {'type': 'scene'}]])
fig.add_trace((lambda v: go.Scatter3d(x=v[0], y=v[1], z=v[2], mode='lines', name='[0]'))(covering(3)), row=1, col=1)
# add a little red dot to show what happens to one individual point
fig.add_trace(go.Scatter3d(x=[point[0]], y=[point[1]], z=[point[2]], mode='markers', name="x", marker=dict(size=5, color='red')), row=1, col=1)

# covering [1]
fig.add_trace((lambda v: go.Scatter3d(x=v[0], y=v[1], z=v[2], mode='lines', name='[1]'))(covering(3, 0, 100)), row=1, col=2)
fig.add_trace(go.Scatter3d(x=[g(point)[0]], y=[g(point)[1]], z=[g(point)[2]], mode='markers', name="g.x", marker=dict(size=5, color='red')), row=1, col=2)

# covering [2]
fig.add_trace((lambda v: go.Scatter3d(x=v[0], y=v[1], z=v[2], mode='lines', name='[2]'))(covering(3, 1/8, 100)), row=1, col=3)
fig.add_trace(go.Scatter3d(x=[g(g(point))[0]], y=[g(g(point))[1]], z=[g(g(point))[2]], mode='markers', name="g.g.x", marker=dict(size=5, color='red')), row=1, col=3)


# legend
fig.update_layout(
	title="Group action of the cyclic group with three elements on our covering space",
)
fig.show()


