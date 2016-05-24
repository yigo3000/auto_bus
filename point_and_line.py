total_points = []#several object of points
arbitrator_index = [0]
class point():
    def __init__(self,current_p,next_p,pre_p):
        '''current_p: string, next_p: list, pre_p: list'''
        self.current_p = current_p
        self.next_p = next_p
        self.pre_p = pre_p
    def set_current_p(self,new_p):
        self.current_p = new_p
        
    def set_next_p(self,new_p):
        self.next_p = new_p
    def set_pre_p(self, new_p):
        self.pre_p = new_p

    def __str__(self):
        return("cur:%s, next:%s, pre:%s" %(self.current_p,self.next_p,self.pre_p))
    
def check_master_point(o_point,   arbitrator_index,total_points):
    if len(o_point.next_p)<=1:
        pass
    elif len(o_point.next_p) > 1:
        for i in total_points:#change all pre_p into this arbitrator
            for j in range(0,len(i.pre_p)):
                if o_point.current_p == i.pre_p[j]:
                    i.pre_p[j] = "arbitrator_%d" %arbitrator_index[0]

        total_points.append(point("arbitrator_%d" %arbitrator_index[0],o_point.next_p,o_point.current_p))#build a new point

        o_point.set_next_p(["arbitrator_%d" %arbitrator_index[0]])

        arbitrator_index[0]+=1

def check_slave_point(o_point,   arbitrator_index,total_points):
    if len(o_point.pre_p)<=1:
        pass
    elif len(o_point.pre_p) >1:
        for i in total_points:#change all pre_p into this arbitrator
            for j in range(0,len(i.next_p)):
                if o_point.current_p == i.next_p[j]:
                    i.next_p[j] = ("arbitrator_%d" %arbitrator_index[0])

        total_points.append(point("arbitrator_%d" %arbitrator_index[0],o_point.current_p,o_point.pre_p))#build a new point
        o_point.set_pre_p(["arbitrator_%d" %arbitrator_index[0]])

        arbitrator_index[0]+=1

total_points.append(point("A",["a","b","e"],[""]))
total_points.append(point("B",["b","c","d"],[""]))
total_points.append(point("C",["a","b"],[""]))
total_points.append(point("a",[""],["A","C"]))
total_points.append(point("b",[""],["A","C"]))
total_points.append(point("c",[""],["B"]))
total_points.append(point("d",[""],["B"]))
total_points.append(point("e",[""],["A"]))
for j in range(0,len(total_points)):
    check_master_point(total_points[j],arbitrator_index,total_points)
for j in range(0,len(total_points)):
    check_slave_point(total_points[j],arbitrator_index,total_points)
for j in total_points:
    print(j)
