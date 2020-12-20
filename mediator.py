from detection import Detection
#from combine import combined
class Mediate:
    det_obj=Detection()
    def stay_to_mediate(self,request):
        things=["ball","bowl","bottle","teddy bear","pen","cell phone","couch"]
        if request in things:
            print("from mediator",request)
            self.det_obj.detect_obj(request)
        elif request=="land":
            self.det_obj.land()
            print("land")
        else:
            print("default request found")
            
if __name__ == "__main__":
    mediate=Mediate()
    mediate.stay_to_mediate("bottle")  
        
        