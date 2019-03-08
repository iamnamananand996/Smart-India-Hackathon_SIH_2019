import pandas as pd
import math

class Market(object):

    def __init__(self):
        self.data =  data = pd.read_csv('state-profit-data.csv')

    
    def State_Crop(self):
        states = self.data.loc[:,'state'].unique()
        crops = self.data.loc[:,'crop'].unique()

        return states,crops
    
    def predict_data(self,state,crop):
        print(state)
        print(crop)
        # data = pd.read_csv('state-profit-data.csv')        
        if len(state) == 0 and len(crop) == 0:
            print('no crop')
        elif len(state) != 0 and crop == 'All':
            result = self.data['state'].str.contains(state)
            result = self.data[result][:]

            lt = []
            for index, row in result.iterrows():
                lst = []
                lst = [row['state'],row['crop'],math.floor(row['profit'])]
                lt.append(lst)

            print(len(result))
        elif len(state) != 0 and crop != 'All':
            result = self.data['state'].str.contains(state)
            result = self.data[result][:]
            result = result[result['crop'] == crop]
            lt = []
            for index, row in result.iterrows():
                lst = []
                lst = [row['state'],row['crop'],row['profit']]
                lt.append(lst)
            print(len(result))
        
        return lt

    # states = data.loc[:,'state'].unique()
    # crops = data.loc[:,'crop'].unique()
    # return render_template('market.html',result=lt,result_len =len(lt),display=True,states=states,crops=crops)