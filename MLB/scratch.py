# import mlb_ML
# import mlb_LR
# from datetime import datetime,timedelta
# import mlb_pred_v2
# date=datetime.now().strftime("%Y-%m-%d")
# yesterday=(datetime.now()-timedelta(days=1)).strftime("%Y-%m-%d")
# # add average rnus to data
#
# # bet on total runs instead of wins for some
# # mlb_ML.get_mlb_prediction('2024-7-4')
#
# if __name__=='__main__':
#     for id in mlb_pred_v2.get_game_ids(date):
#         print(mlb_pred_v2.get_top_three_batters_ops(id))
#     game_ids=[game_id for game_id in mlb_pred_v2.get_game_ids(date)]
#     ml_model=[mlb_ML.load_mlb_model() for id in game_ids]
#     ml_results=[result for result in mlb_pred_v2.use_process_pool(mlb_ML.get_mlb_prediction,[game_ids,ml_model],6) if result]
#     lr_model=[mlb_LR.load_mlb_model() for id in game_ids]
#     lr_results=[result for result in mlb_pred_v2.use_process_pool(mlb_LR.get_mlb_prediction,[game_ids,lr_model],6) if result]
#     for (away,home,(a_pred,h_pred)),(away1,_,(a_pred1,h_pred1)) in zip(ml_results,lr_results):
#         if away1==away:
#             print(f'{away}:{a_pred+a_pred1}  {home}:{h_pred+h_pred1}')

